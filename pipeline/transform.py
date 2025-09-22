# python
"""
Transform raw responses in `raw_stock_source` into rows for `stock_basic` and upsert into DB.

Usage examples:
  - Build/merge for specific symbols:
      from pipeline.transform import upsert_stock_basic_from_raws
      upsert_stock_basic_from_raws(["000001.SZ", "600000.SH"])

  - Build for all symbols present in raw_stock_source:
      from pipeline.transform import upsert_stock_basic_from_raws
      upsert_stock_basic_from_raws()
"""
from typing import Dict, Iterable, List, Optional
import json

import pandas as pd
from pipeline.helper import (
    ENGINE,
    get_raw_stock_source,
    upsert_df,
    save_df,
    get_engine,
)
from sqlalchemy import text


def _flatten(d: Dict, parent: str = "", sep: str = "_") -> Dict:
    """
    Flatten a nested dict one or more levels deep into a flat dict with joined keys.
    Example: {'a': {'b': 1}} -> {'a_b': 1}
    """
    out: Dict = {}
    for k, v in d.items():
        key = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            out.update(_flatten(v, parent=key, sep=sep))
        else:
            out[key] = v
    return out


def _parse_raw_text(raw_text: str) -> Dict:
    """
    Try to parse raw_text as JSON and return a dict; if parsing fails, return {'_raw': raw_text}.
    """
    if raw_text is None:
        return {}
    try:
        parsed = json.loads(raw_text)
        # if the parsed object is a list, pick first element if it's a dict; otherwise store as _raw_list
        if isinstance(parsed, list):
            if len(parsed) == 0:
                return {}
            # prefer merging first element if it's a dict
            if isinstance(parsed[0], dict):
                parsed = parsed[0]
            else:
                return {"_raw_list": parsed}
        if isinstance(parsed, dict):
            return _flatten(parsed)
        # otherwise primitive
        return {"_value": parsed}
    except Exception:
        # fallback: not JSON; return raw string
        return {"_raw_text": raw_text}


def build_stock_basic_df(
    symbols: Optional[Iterable[str]] = None,
    endpoints: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    limit_per_endpoint: int = 1,
) -> pd.DataFrame:
    """
    Construct a DataFrame suitable for upserting into `stock_basic` by merging
    latest raw responses for each (symbol, source, endpoint).

    - symbols: iterable of symbol strings. If None, gather distinct non-null symbols from raw_stock_source.
    - endpoints: list of endpoint names to consider (strings stored in raw_stock_source.endpoint).
                 Default includes common endpoints used by akshare/efinance.
    - sources: filter by data sources (e.g. ['akshare','efinance']); default both.
    - limit_per_endpoint: how many latest rows to fetch per (symbol,source,endpoint). Default 1.

    The merging strategy:
      - For each (symbol, source, endpoint), fetch up to `limit_per_endpoint` rows ordered by fetched_at desc.
      - Parse raw JSON/text, flatten fields, and prefix keys by "{source}__{endpoint}__" to avoid collisions.
      - Merge all fields for same symbol; later values override earlier ones.
      - Ensure `symbol` column exists (must be the primary key).
    """
    if endpoints is None:
        endpoints = [
            "stock_individual_info_em",
            "stock.get_base_info",
            "stock_individual_basic_info_xq",
        ]
    if sources is None:
        sources = ["akshare", "efinance"]

    engine = get_engine()

    # determine symbols if not provided
    if symbols is None:
        q = "SELECT DISTINCT symbol FROM raw_stock_source WHERE symbol IS NOT NULL"
        df_sym = pd.read_sql_query(text(q), engine)
        symbols = df_sym["symbol"].dropna().astype(str).tolist()

    rows: List[Dict] = []
    for symbol in symbols:
        merged: Dict = {"symbol": symbol}
        for source in sources:
            for endpoint in endpoints:
                try:
                    df = get_raw_stock_source(
                        symbol=symbol, source=source, endpoint=endpoint, limit=limit_per_endpoint, as_df=True
                    )
                except Exception:
                    df = pd.DataFrame()
                if df is None or df.empty:
                    continue
                # iterate rows in time-desc order (we requested latest first)
                for _, r in df.iterrows():
                    raw_text = r.get("raw") if "raw" in r else None
                    parsed = _parse_raw_text(raw_text)
                    # prefix keys to avoid collisions and make provenance clear
                    prefix = f"{source}__{endpoint}__"
                    for k, v in parsed.items():
                        merged_key = f"{prefix}{k}"
                        # later parsed values override earlier ones
                        merged[merged_key] = v
        rows.append(merged)

    if not rows:
        return pd.DataFrame(columns=["symbol"])

    df_out = pd.DataFrame(rows)
    # normalize columns: ensure symbol is first
    cols = list(df_out.columns)
    if "symbol" in cols:
        cols = ["symbol"] + [c for c in cols if c != "symbol"]
        df_out = df_out[cols]
    return df_out


def upsert_stock_basic_from_raws(
    symbols: Optional[Iterable[str]] = None,
    endpoints: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    limit_per_endpoint: int = 1,
):
    """
    Build DataFrame via build_stock_basic_df and upsert into `stock_basic` table using `symbol` as conflict key.
    """
    df = build_stock_basic_df(
        symbols=symbols, endpoints=endpoints, sources=sources, limit_per_endpoint=limit_per_endpoint
    )
    if df.empty:
        return
    # Ensure stock_basic table exists (create empty if not)
    with ENGINE.begin() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS stock_basic (
              symbol TEXT NOT NULL PRIMARY KEY
            );
            """
            )
        )
    # Use upsert_df helper to merge rows based on symbol
    upsert_df(df, "stock_basic", conflict_keys=["symbol"])


if __name__ == "__main__":
    # CLI quick-run: process all symbols discovered in raw_stock_source
    upsert_stock_basic_from_raws()
