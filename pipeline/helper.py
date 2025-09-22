from pathlib import Path
from typing import List, Optional

import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text

DB_FILE = Path("data/marketseer.db")
DB_FILE.parent.mkdir(parents=True, exist_ok=True)
ENGINE = create_engine(f"sqlite:///{DB_FILE.resolve()}", future=True)


def get_engine():
    """Return the shared SQLAlchemy engine."""
    return ENGINE


def save_df(
    df: pd.DataFrame,
    table: str,
    if_exists: str = "append",
    index: bool = False,
    chunksize: Optional[int] = None,
):
    """
    Save DataFrame to table using pandas.to_sql.

    if_exists: 'replace' | 'append' | 'fail'
    """
    df.to_sql(table, ENGINE, if_exists=if_exists, index=index, chunksize=chunksize)


def load_df(table: Optional[str] = None, query: Optional[str] = None) -> pd.DataFrame:
    """
    Load a table or run a custom SQL query and return a DataFrame.
    Either `table` or `query` must be provided. If both provided, `query` takes precedence.
    """
    if query:
        return pd.read_sql_query(text(query), ENGINE)
    if table:
        return pd.read_sql_table(table, ENGINE)
    raise ValueError("Either table or query must be provided")


def upsert_df(
    df: pd.DataFrame, table: str, conflict_keys: List[str], update_columns: Optional[List[str]] = None
):
    """
    Upsert DataFrame into `table` using SQLite ON CONFLICT.
    Strategy:
      1. Write df into a temp table named _tmp_{table}
      2. Execute INSERT ... SELECT ... ON CONFLICT(conflict_keys) DO UPDATE SET ...
      3. Drop temp table

    Notes:
    - conflict_keys must be one or more columns that form a UNIQUE constraint in the target table.
    - If the target table does not exist, it will be created with the same schema as the temp table (empty).
    - This function uses SQLAlchemy engine and runs the merge within a transaction.
    """
    if df.empty:
        return

    temp = f"_tmp_{table}"
    # write temp table
    df.to_sql(temp, ENGINE, if_exists="replace", index=False)

    cols = list(df.columns)
    insert_cols = ", ".join([f'"{c}"' for c in cols])
    select_cols = ", ".join([f'"{c}"' for c in cols])

    if update_columns is None:
        update_columns = [c for c in cols if c not in conflict_keys]

    if update_columns:
        # Ensure target table exists and has columns from temp before merging.
        with ENGINE.begin() as _conn:
            _conn.execute(text(f'CREATE TABLE IF NOT EXISTS "{table}" AS SELECT * FROM "{temp}" WHERE 0'))
            tmp_info = _conn.execute(text(f"PRAGMA table_info('{temp}')")).mappings().all()
            target_info = _conn.execute(text(f"PRAGMA table_info('{table}')")).mappings().all()
            tmp_cols = [row["name"] for row in tmp_info]
            target_cols = [row["name"] for row in target_info]
            missing_cols = [c for c in tmp_cols if c not in target_cols]
            for col in missing_cols:
                _conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{col}" TEXT'))

        # Always use explicit delete+insert to avoid relying on SQLite UPSERT syntax compatibility.
        if len(conflict_keys) == 1:
            pk_col = conflict_keys[0]
            delete_sql = f'DELETE FROM "{table}" WHERE "{pk_col}" IN (SELECT "{pk_col}" FROM "{temp}")'
        else:
            join_conds = " AND ".join([f'"{table}"."{k}" = "{temp}"."{k}"' for k in conflict_keys])
            delete_sql = f'DELETE FROM "{table}" WHERE EXISTS (SELECT 1 FROM "{temp}" WHERE {join_conds})'
        # perform delete + insert: delete conflicting rows then append temp rows via pandas
        with ENGINE.begin() as _conn:
            _conn.execute(text(delete_sql))
        # read temp table and append to target using pandas to_sql to avoid column-name mismatches
        temp_df = pd.read_sql_table(temp, ENGINE)
        temp_df.to_sql(table, ENGINE, if_exists="append", index=False)
        # skip executing `sql` below since we've already merged
        sql = None
    else:
        # no updatable columns: ignore conflicts
        sql = f'INSERT OR IGNORE INTO "{table}" ({insert_cols}) SELECT {select_cols} FROM "{temp}"'

    with ENGINE.begin() as conn:
        # ensure target table exists with same columns (create empty from temp)
        conn.execute(text(f'CREATE TABLE IF NOT EXISTS "{table}" AS SELECT * FROM "{temp}" WHERE 0'))
        # Ensure target has any columns present in the temp table; add missing columns as TEXT
        tmp_info = conn.execute(text(f"PRAGMA table_info('{temp}')")).mappings().all()
        target_info = conn.execute(text(f"PRAGMA table_info('{table}')")).mappings().all()
        tmp_cols = [row["name"] for row in tmp_info]
        target_cols = [row["name"] for row in target_info]
        missing_cols = [c for c in tmp_cols if c not in target_cols]
        for col in missing_cols:
            conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{col}" TEXT'))
        if sql is not None:
            conn.execute(text(sql))
        conn.execute(text(f'DROP TABLE IF EXISTS "{temp}"'))


def get_raw_stock_source(
    symbol: Optional[str] = None,
    source: Optional[str] = None,
    endpoint: Optional[str] = None,
    since: Optional[int] = None,
    until: Optional[int] = None,
    limit: Optional[int] = None,
    as_df: bool = True,
):
    """
    Query rows from raw_stock_source.

    Returns a pandas.DataFrame if as_df is True (default), otherwise returns a list of dicts.
    Filters are applied when their corresponding argument is not None.

    Parameters:
      symbol: filter by symbol (exact match)
      source: filter by source (exact match)
      endpoint: filter by endpoint (exact match)
      since: include rows with fetched_at >= since (unix timestamp)
      until: include rows with fetched_at <= until (unix timestamp)
      limit: maximum number of rows to return
      as_df: whether to return a pandas.DataFrame (True) or list of dicts (False)
    """
    where_clauses = ["1=1"]
    params = {}

    if symbol is not None:
        where_clauses.append("symbol = :symbol")
        params["symbol"] = symbol
    if source is not None:
        where_clauses.append("source = :source")
        params["source"] = source
    if endpoint is not None:
        where_clauses.append("endpoint = :endpoint")
        params["endpoint"] = endpoint
    if since is not None:
        where_clauses.append("fetched_at >= :since")
        params["since"] = int(since)
    if until is not None:
        where_clauses.append("fetched_at <= :until")
        params["until"] = int(until)

    where_sql = " AND ".join(where_clauses)
    sql = f"SELECT id, symbol, source, endpoint, raw, fetched_at FROM raw_stock_source WHERE {where_sql} ORDER BY fetched_at DESC"
    if limit is not None and int(limit) > 0:
        sql = sql + f" LIMIT {int(limit)}"

    if as_df:
        # pandas can accept SQLAlchemy text and params
        return pd.read_sql_query(text(sql), ENGINE, params=params)
    else:
        with ENGINE.begin() as conn:
            result = conn.execute(text(sql), params)
            rows = [dict(row) for row in result.mappings().all()]
        return rows


def insert_raw_stock_source(
    symbol: Optional[str],
    source: str,
    endpoint: str,
    raw_text: str,
    fetched_at: Optional[int] = None,
    conn=None,
):
    """
    Insert a single record into raw_stock_source.

    Parameters:
      symbol: associated symbol (or None)
      source: data source name, e.g. "akshare" or "efinance"
      endpoint: client endpoint name, e.g. "stock_individual_basic_info_xq"
      raw_text: raw JSON/text string returned by the client
      fetched_at: unix timestamp (int). If None, use current time.
      conn: optional SQLAlchemy Connection (will use ENGINE.begin() if not provided)
    """
    import time

    if fetched_at is None:
        fetched_at = int(time.time())

    sql = text(
        """
    INSERT INTO raw_stock_source (symbol, source, endpoint, raw, fetched_at)
    VALUES (:symbol, :source, :endpoint, :raw, :fetched_at)
    """
    )
    params = {
        "symbol": symbol,
        "source": source,
        "endpoint": endpoint,
        "raw": raw_text,
        "fetched_at": int(fetched_at),
    }

    if conn is not None:
        # caller provided a connection/transaction
        conn.execute(sql, params)
    else:
        # use a short-lived transaction
        with ENGINE.begin() as _conn:
            _conn.execute(sql, params)
