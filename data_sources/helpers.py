from __future__ import annotations
from typing import Union, Any, Callable, Literal
from datetime import date, datetime
from functools import wraps
import os
import time
import pandas as pd

from utils.logger import  get_data_sources_logger


# ============ Logging ============
logger = get_data_sources_logger("datasource.efinance")


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

# helpers.py
from typing import Literal

def detect_market_prefix(stock_code: str) -> Literal["SH", "SZ"]:
    """
    Robust market detector for CN A/B shares.
    - Prefer explicit prefix/suffix in the original input.
    - Match known numeric prefixes for SH/SZ.
    - Fallback by first digit.
    """
    s = (stock_code or "").strip().lower()

    # 1) Respect explicit prefix/suffix in original input
    if s.startswith("sh") or s.endswith(".sh"):
        return "SH"
    if s.startswith("sz") or s.endswith(".sz"):
        return "SZ"

    # 2) Normalize to pure 6-digit code
    c = normalize_stock_code(stock_code)

    # 3) Explicit prefix tables
    sh_prefixes = ("600", "601", "603", "605", "688", "900")  # SH A & B, STAR
    sz_prefixes = ("000", "001", "002", "003", "200", "300", "301")  # SZ A & B, ChiNext

    if any(c.startswith(p) for p in sh_prefixes):
        return "SH"
    if any(c.startswith(p) for p in sz_prefixes):
        return "SZ"

    # 4) Fallback (keep simple and practical)
    # - SH: codes starting with '6' or '9' (6xx A/STAR, 900 B)
    # - otherwise SZ
    return "SH" if c[0] in ("6", "9") else "SZ"


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
                        logger.bind(fn=fn.__name__).info(
                            "ok rows={} cols={} elapsed={:.1f}ms args={} kwargs={}",
                            len(df),
                            len(df.columns),
                            elapsed,
                            args,
                            kwargs,
                        )
                    else:
                        logger.bind(fn=fn.__name__).info(
                            "ok type={} elapsed={:.1f}ms args={} kwargs={}",
                            type(df),
                            elapsed,
                            args,
                            kwargs,
                        )
                    if _cache is not None and key is not None:
                        _cache[key] = (time.time(), df)
                    return df
                except Exception as e:
                    attempt += 1
                    if attempt > retries:
                        logger.bind(fn=fn.__name__).error(
                            "failed after {} tries: {}", attempt, repr(e)
                        )
                        raise
                    sleep_s = backoff ** attempt
                    logger.bind(fn=fn.__name__).warning(
                        "retry {}/{} in {:.2f}s: {}", attempt, retries, sleep_s, repr(e)
                    )
                    time.sleep(sleep_s)
        return wrapper
    return deco
