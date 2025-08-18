from __future__ import annotations
from typing import Literal, Union, Any, Callable
from datetime import date, datetime
from functools import wraps
import os
import time
import logging

import pandas as pd
import akshare as ak

# ============ Logging ============

logger = logging.getLogger("akshare_client")
if not logger.handlers:
    logging.basicConfig(
        level=os.getenv("AK_CLIENT_LOG_LEVEL", "INFO"),  # 操作系统环境变量中找 "AK_CLIENT_LOG_LEVEL" 这个变量如果找到了，就使用它的值（比如 "DEBUG"、"WARNING" 等）如果没找到，就默认使用 "INFO"
        format="%(asctime)s | %(levelname)s | %(message)s",  # 每条日志输出格式：“2025-08-17 12:00:00,123 | INFO | 这是日志内容”
    )


# ============ Types ============

DateLike = Union[str, date, datetime]


# ============ Utils ============

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


# ============ Spot ============

"""上证 A 股现货行情"""
@safe_call(cache=True)
def get_sh_a_spot() -> pd.DataFrame:
    return ak.stock_sh_a_spot_em()

"""A 股（沪深）整体现货行情"""
@safe_call(cache=True)
def get_zh_a_spot() -> pd.DataFrame:
    return ak.stock_zh_a_spot_em()


# ============ Profiles ============

""" 东方财富-个股基础信息（item/value 结构）"""
@safe_call(cache=True)
def get_profile_em(stock_code: str) -> pd.DataFrame:
    code = normalize_stock_code(stock_code)
    return ak.stock_individual_info_em(symbol=code)

"""雪球-个股基础信息（AkShare 封装）"""
@safe_call(cache=True)
def get_profile_xq(stock_code: str) -> pd.DataFrame:
    code = normalize_stock_code(stock_code)
    market = detect_market_prefix(code)
    symbol = f"{market}{code}"
    return ak.stock_individual_basic_info_xq(symbol)


# ============ LHB - EastMoney ============

"""东方财富网-数据中心-龙虎榜单-龙虎榜详情"""
@safe_call(cache=False)
def get_lhb_detail(start_date: DateLike, end_date: DateLike) -> pd.DataFrame:
    sd = to_em_date(start_date)
    ed = to_em_date(end_date)
    return ak.stock_lhb_detail_em(start_date=sd, end_date=ed)

"""东方财富网-数据中心-龙虎榜单-个股上榜统计"""
@safe_call(cache=True)
def get_lhb_stock_statistic(stock_code: str) -> pd.DataFrame:
    code = normalize_stock_code(stock_code)
    return ak.stock_lhb_stock_statistic_em(symbol=code)

"""东方财富网-数据中心-龙虎榜单-机构买卖每日统计"""
@safe_call(cache=True)
def get_lhb_institution_stat() -> pd.DataFrame:
    return ak.stock_lhb_jgmmtj_em()

"""东方财富网-数据中心-龙虎榜单-机构席位追踪"""
@safe_call(cache=True)
def get_lhb_institution_tracking() -> pd.DataFrame:
    return ak.stock_lhb_jgstatistic_em()

"""东方财富网-数据中心-龙虎榜单-每日活跃营业部"""
@safe_call(cache=True)
def get_lhb_active_broker() -> pd.DataFrame:
    return ak.stock_lhb_hyyyb_em()

"""东方财富网-数据中心-龙虎榜单-营业部历史交易明细-营业部交易明细"""
@safe_call(cache=True)
def get_lhb_broker_detail(broker_code: str) -> pd.DataFrame:
    return ak.stock_lhb_yyb_detail_em(symbol=broker_code)

"""东方财富网-数据中心-龙虎榜单-营业部排行"""
@safe_call(cache=True)
def get_lhb_broker_rank() -> pd.DataFrame:
    return ak.stock_lhb_yybph_em()

"""东方财富网-数据中心-龙虎榜单-营业部统计"""
@safe_call(cache=True)
def get_lhb_broker_statistic() -> pd.DataFrame:
    return ak.stock_lhb_traderstatistic_em()

"""东方财富网-数据中心-龙虎榜单-个股龙虎榜详情"""
@safe_call(cache=True)
def get_lhb_stock_detail(stock_code: str) -> pd.DataFrame:
    code = normalize_stock_code(stock_code)
    return ak.stock_lhb_stock_detail_em(symbol=code)

"""龙虎榜-营业部排行-上榜次数最多"""
@safe_call(cache=True)
def get_lhb_broker_most() -> pd.DataFrame:
    return ak.stock_lh_yyb_most()

"""龙虎榜-营业部排行-资金实力最强"""
@safe_call(cache=True)
def get_lhb_broker_capital() -> pd.DataFrame:
    return ak.stock_lh_yyb_capital()

"""龙虎榜-营业部排行-抱团操作实力"""
@safe_call(cache=True)
def get_lhb_broker_control() -> pd.DataFrame:
    return ak.stock_lh_yyb_control()


# ============ LHB - Sina ============

"""新浪财经-龙虎榜-每日详情"""
@safe_call(cache=False)
def get_lhb_detail_daily_sina(date_: DateLike) -> pd.DataFrame:
    d = to_sina_date(date_)
    return ak.stock_lhb_detail_daily_sina(date=d)

"""新浪财经-龙虎榜-个股上榜统计"""
@safe_call(cache=True)
def get_lhb_stock_statistic_sina(stock_code: str) -> pd.DataFrame:
    # 新浪这里就是 symbol，兼容 '600000' 或 'sh600000'
    symbol = stock_code.strip()
    if symbol.isdigit() and len(symbol) == 6:
        # 允许纯 6 位，AkShare 会处理，但也可按需拼前缀
        pass
    return ak.stock_lhb_ggtj_sina(symbol=symbol)

"""新浪财经-龙虎榜-营业上榜统计"""
@safe_call(cache=True)
def get_lhb_broker_statistic_sina(broker_symbol: str) -> pd.DataFrame:
    return ak.stock_lhb_yytj_sina(symbol=broker_symbol)

"""新浪财经-龙虎榜-机构席位追踪"""
@safe_call(cache=True)
def get_lhb_institution_tracking_sina(stock_symbol: str) -> pd.DataFrame:
    return ak.stock_lhb_jgzz_sina(symbol=stock_symbol)

"""新浪财经-龙虎榜-机构席位成交明细"""
@safe_call(cache=True)
def get_lhb_institution_detail_sina() -> pd.DataFrame:
    return ak.stock_lhb_jgmx_sina()


__all__ = [
    "get_sh_a_spot", "get_zh_a_spot",
    "get_profile_em", "get_profile_xq",
    "get_lhb_detail", "get_lhb_stock_statistic", "get_lhb_institution_stat",
    "get_lhb_institution_tracking", "get_lhb_active_broker",
    "get_lhb_broker_detail", "get_lhb_broker_rank", "get_lhb_broker_statistic",
    "get_lhb_stock_detail",
    "get_lhb_broker_most", "get_lhb_broker_capital", "get_lhb_broker_control",
    "get_lhb_detail_daily_sina", "get_lhb_stock_statistic_sina",
    "get_lhb_broker_statistic_sina", "get_lhb_institution_tracking_sina",
    "get_lhb_institution_detail_sina",
]











