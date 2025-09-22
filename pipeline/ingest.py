# python
"""
Ingest raw responses from akshare / efinance endpoints into raw_stock_source.

Example usage:
  # ingest for specific symbols
  python -m pipeline.ingest --symbols 000001.SZ 600000.SH

  # ingest default sample symbols
  python -m pipeline.ingest

Notes:
- This script uses pipeline.clients.AkshareClient and EfinanceClient.
- It will call endpoints with several common param names (symbol, code, stock) to maximize compatibility.
- Each raw response is json.dumps(...) and written via insert_raw_stock_source.
"""
import argparse
import json
import logging
import time
from typing import Iterable, List, Optional
import pandas as pd

from pipeline.clients.akshare_client import AkshareClient
from pipeline.clients.efinance_client import EfinanceClient
from pipeline.helper import insert_raw_stock_source, get_engine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _try_fetch_with_param_names(client, endpoint: str, symbol: Optional[str]):
    """
    Try calling client.fetch(endpoint, ...) with various param names.
    Accepts `symbol` as None, a single string, or an iterable of candidate strings.
    Return the raw result object (not string). Raise last exception if all fail.
    """
    # Normalize symbols into a list of candidates to try (preserve order)
    if symbol is None:
        symbol_candidates = [None]
    elif isinstance(symbol, (list, tuple)):
        symbol_candidates = list(symbol)
    else:
        symbol_candidates = [symbol]

    last_exc = None
    for sym in symbol_candidates:
        if sym is not None:
            # Choose param candidates based on client type to avoid passing
            # unsupported kwargs (e.g. efinance.get_base_info doesn't accept "code")
            if isinstance(client, EfinanceClient):
                param_candidates = [
                    {"stock_codes": sym},
                    {"stock_codes": [sym]},
                    {"stock": sym},
                    {"symbol": sym},
                    {"ticker": sym},
                ]
            elif isinstance(client, AkshareClient):
                param_candidates = [
                    {"symbol": sym},
                    {"code": sym},
                    {"stock": sym},
                    {"ticker": sym},
                    {"stock_codes": sym},
                    {"stock_codes": [sym]},
                ]
            else:
                # fallback: try common names but avoid placing "code" first
                param_candidates = [
                    {"symbol": sym},
                    {"stock": sym},
                    {"ticker": sym},
                    {"stock_codes": sym},
                    {"stock_codes": [sym]},
                    {"code": sym},
                ]
        else:
            param_candidates = [{}]

        for params in param_candidates:
            try:
                return client.fetch(endpoint, **params)
            except Exception as e:
                last_exc = e
                logger.debug("fetch failed for %s with params %s: %s", endpoint, params, e)
                continue

    # try calling without params as a last resort
    try:
        return client.fetch(endpoint)
    except Exception as e:
        logger.debug("fetch without params failed for %s: %s", endpoint, e)
        if last_exc is not None:
            raise last_exc
        raise


def _symbol_variants(symbol: Optional[str]):
    """
    Produce symbol variants (full, plain, prefixed) from inputs like:
      - "002104.SZ" => ("002104.SZ", "002104", "SZ002104")
      - "SZ002104"   => (None, "002104", "SZ002104")
      - "002104"     => (None, "002104", "SZ002104")  # infer exchange from code
    Returns a tuple (full, plain, prefixed).

    Exchange inference rules:
      - If plain code starts with '6' -> SH (沪市)
      - Otherwise -> SZ (深市)
    """
    if symbol is None:
        return (None, None, None)
    full = symbol
    plain = None
    prefixed = None
    if "." in symbol:
        code, exch = symbol.split(".", 1)
        plain = code
        prefixed = exch.upper() + code
    elif len(symbol) >= 3 and symbol[:2].isalpha():
        # already prefixed like SZ002104
        prefixed = symbol
        plain = symbol[2:]
        full = None
    else:
        # plain code like "002104" or "600000"
        plain = symbol
        full = None
        # infer exchange when not provided
        if len(plain) >= 1:
            if plain[0] == "6":
                exch = "SH"
            else:
                exch = "SZ"
            prefixed = exch + plain
    return (full, plain, prefixed)


def ingest_for_symbol(
    symbol: Optional[str],
    ak_endpoints: List[str],
    ef_endpoints: List[str],
    limit_per_endpoint: int = 1,
    delay_seconds: float = 0.0,
):
    """
    Fetch endpoints for one symbol and write raw responses into raw_stock_source.
    If symbol is None, endpoints are fetched without symbol param where possible.

    This version adapts the symbol format per-endpoint:
      - akshare.stock_individual_info_em expects plain code (e.g. "002104")
      - akshare.stock_individual_basic_info_xq expects prefixed code (e.g. "SZ002104" or "SH002104")
      - efinance.stock.get_base_info expects plain code (e.g. "002104")
    For unknown endpoints we try multiple candidates in order.
    """
    ak = AkshareClient()
    ef = EfinanceClient()

    full, plain, prefixed = _symbol_variants(symbol)

    def _candidates_for_endpoint(ep: str, source: str):
        """
        Return a symbol or iterable of symbol candidates tailored for the endpoint.
        """
        # akshare specific rules
        if source == "akshare":
            if ep == "stock_individual_info_em":
                return plain
            if ep == "stock_individual_basic_info_xq":
                return prefixed
            # unknown ak endpoint: try full, plain, prefixed
            return [v for v in (full, plain, prefixed) if v is not None]
        # efinance specific rules
        if source == "efinance":
            if ep == "stock.get_base_info":
                return plain
            # unknown ef endpoint: try full, plain, prefixed
            return [v for v in (full, plain, prefixed) if v is not None]
        # fallback: try all variants
        return [v for v in (full, plain, prefixed) if v is not None]

    # akshare endpoints
    for ep in ak_endpoints:
        sym_arg = _candidates_for_endpoint(ep, "akshare")
        try:
            res = _try_fetch_with_param_names(ak, ep, sym_arg)
            # convert pandas objects to JSON-serializable python structures
            try:
                if isinstance(res, pd.DataFrame):
                    # If DataFrame has a single column but meaningful index (not a RangeIndex),
                    # convert index->value mapping so keys are preserved.
                    if res.shape[1] == 1 and not isinstance(res.index, pd.RangeIndex):
                        col0 = res.columns[0]
                        payload = dict(zip(res.index.astype(str).tolist(), res.iloc[:, 0].tolist()))
                    else:
                        # Typical table-like DataFrame -> list of records
                        payload = res.to_dict(orient="records")
                elif isinstance(res, pd.Series):
                    # Series: index -> value mapping for a single record
                    payload = res.to_dict()
                else:
                    payload = res
            except Exception:
                payload = res
            raw_text = json.dumps(payload, ensure_ascii=False)
            insert_raw_stock_source(
                symbol=symbol, source="akshare", endpoint=ep, raw_text=raw_text, fetched_at=int(time.time())
            )
            logger.info("Inserted akshare %s for %s (used %s)", ep, symbol, sym_arg)
        except Exception as e:
            logger.warning("Failed akshare %s for %s (used %s): %s", ep, symbol, sym_arg, e)

        if delay_seconds:
            time.sleep(delay_seconds)

    # efinance endpoints
    for ep in ef_endpoints:
        sym_arg = _candidates_for_endpoint(ep, "efinance")
        try:
            res = _try_fetch_with_param_names(ef, ep, sym_arg)
            # convert pandas objects to JSON-serializable python structures
            try:
                if isinstance(res, pd.DataFrame):
                    # If DataFrame has a single column but meaningful index (not a RangeIndex),
                    # convert index->value mapping so keys are preserved.
                    if res.shape[1] == 1 and not isinstance(res.index, pd.RangeIndex):
                        col0 = res.columns[0]
                        payload = dict(zip(res.index.astype(str).tolist(), res.iloc[:, 0].tolist()))
                    else:
                        # Typical table-like DataFrame -> list of records
                        payload = res.to_dict(orient="records")
                elif isinstance(res, pd.Series):
                    # Series: index -> value mapping for a single record
                    payload = res.to_dict()
                else:
                    payload = res
            except Exception:
                payload = res
            raw_text = json.dumps(payload, ensure_ascii=False)
            insert_raw_stock_source(
                symbol=symbol, source="efinance", endpoint=ep, raw_text=raw_text, fetched_at=int(time.time())
            )
            logger.info("Inserted efinance %s for %s (used %s)", ep, symbol, sym_arg)
        except Exception as e:
            logger.warning("Failed efinance %s for %s (used %s): %s", ep, symbol, sym_arg, e)

        if delay_seconds:
            time.sleep(delay_seconds)


def ingest_symbols(
    symbols: Optional[Iterable[str]] = None,
    ak_endpoints: Optional[List[str]] = None,
    ef_endpoints: Optional[List[str]] = None,
    delay_seconds: float = 0.0,
):
    """
    Ingest for a list of symbols. If symbols is None, uses a small built-in default list.
    """
    if ak_endpoints is None:
        ak_endpoints = [
            "stock_individual_info_em",
            "stock_individual_basic_info_xq",
        ]
    if ef_endpoints is None:
        ef_endpoints = [
            "stock.get_base_info",
        ]

    if symbols is None:
        symbols = ["000001.SZ", "600000.SH"]

    for s in symbols:
        ingest_for_symbol(s, ak_endpoints, ef_endpoints, delay_seconds=delay_seconds)


def _parse_args():
    p = argparse.ArgumentParser(
        description="Ingest raw responses from akshare/efinance into raw_stock_source"
    )
    p.add_argument("--symbols", nargs="+", help="Symbols to ingest, e.g. 000001.SZ")
    p.add_argument("--delay", type=float, default=0.0, help="Delay between requests (seconds)")
    return p.parse_args()


def main():
    args = _parse_args()
    # ensure DB exists / engine reachable
    _ = get_engine()
    ingest_symbols(symbols=args.symbols, delay_seconds=args.delay)


if __name__ == "__main__":
    main()
