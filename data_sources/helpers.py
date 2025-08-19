from __future__ import annotations
from typing import Union, Any, Callable, Literal
from datetime import date, datetime
from functools import wraps
import os
import time
import pandas as pd


def normalize_stock_code(code: str) -> str:
    """Return 6-digit numeric stock code. Accepts 'sh600000', 'SZ000001', '000001.SZ'."""
    s = (code or "").strip()
    s = s.replace(".", "").lower()
    # remove possible prefixes
    if s.startswith(("sh", "sz")):
        s = s[2:]
    # remove possible suffixes (e.g., 600000ss or 000001sz)
    s = s.replace("ss", "").replace("sz", "")
    # keep digits only
    s = "".join(ch for ch in s if ch.isdigit())
    if len(s) != 6:
        raise ValueError(f"Invalid stock code: {code!r}")
    return s

def detect_market_prefix(stock_code: str) -> Literal["SH", "SZ"]:
    """
    市场前缀推断（A股常见规则）：
    - 上交所：600/601/603/605/688 开头 -> SH
    - 深交所：000/001/002/003/300 开头 -> SZ
    其余默认 SZ（可按需扩充）
    """
    c = normalize_stock_code(stock_code)
    if c.startswith(("600", "601", "603", "605", "688")):
        return "SH"
    return "SZ"

def to_em_date(d: DateLike) -> str:
    """YYYYMMDD for EastMoney"""
    if isinstance(d, datetime):
        return d.strftime("%Y%m%d")
    if isinstance(d, date):
        return d.strftime("%Y%m%d")
    s = str(d).strip()
    if "-" in s:
        return s.replace("-", "")
    if len(s) == 8 and s.isdigit():
        return s
    raise ValueError(f"Invalid EM date: {d!r}")

def to_sina_date(d: DateLike) -> str:
    """YYYY-MM-DD for Sina."""
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    if isinstance(d, date):
        return d.strftime("%Y-%m-%d")
    s = str(d).strip()
    if len(s) == 8 and s.isdigit():  # 20250115 -> 2025-01-15
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    if len(s) == 10 and s.count("-") == 2:
        return s
    raise ValueError(f"Invalid SINA date: {d!r}")


# ============ Types ============
DateLike = Union[str, date, datetime]


# ============ Decorators ============

def safe_call(retries: int = 2, backoff: float = 1.6, cache: bool = False):
    """
    轻量容错（带可选缓存）：
    - retries/backoff: 简单退避
    - cache: 通过 AK_CLIENT_CACHE_TTL 启用/禁用（秒）
    """
    ttl = int(os.getenv("AK_CLIENT_CACHE_TTL", "0") or 0)
    _cache: dict[str, tuple[float, Any]] = {} if (cache and ttl > 0) else None

    def deco(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = None
            if _cache is not None:
                key = f"{fn.__name__}|{args!r}|{sorted(kwargs.items())!r}"
                hit = _cache.get(key)
                if hit and (time.time() - hit[0] <= ttl):
                    return hit[1]

            t0 = time.time()
            attempt = 0
            while True:
                try:
                    df = fn(*args, **kwargs)
                    elapsed = (time.time() - t0) * 1000
                    if isinstance(df, pd.DataFrame):
                        logger.info(
                            f"{fn.__name__} ok rows={len(df)} cols={len(df.columns)} "
                            f"elapsed={elapsed:.1f}ms args={args!r} kwargs={kwargs!r}"
                        )
                    else:
                        logger.info(
                            f"{fn.__name__} ok type={type(df)} elapsed={elapsed:.1f}ms"
                        )
                    if _cache is not None and key is not None:
                        _cache[key] = (time.time(), df)
                    return df
                except Exception as e:
                    attempt += 1
                    if attempt > retries:
                        logger.error(f"{fn.__name__} failed after {attempt} tries: {e!r}")
                        raise
                    sleep_s = backoff ** attempt
                    logger.warning(f"{fn.__name__} retry {attempt}/{retries} in {sleep_s:.2f}s: {e!r}")
                    time.sleep(sleep_s)
        return wrapper
    return deco
