from __future__ import annotations
import os
import pandas as pd
import akshare as ak
from utils.logger import get_data_sources_logger
from data_sources.helpers import (
    DateLike, normalize_stock_code, detect_market_prefix,
    to_em_date, to_sina_date, safe_call
)

# ============ Logging ============
logger = get_data_sources_logger("akshare_client")


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
def get_lhb_stock_statistic(period: Literal["近一月", "近三月", "近六月", "近一年"]) -> pd.DataFrame:
    return ak.stock_lhb_stock_statistic_em(symbol=period)

"""东方财富网-数据中心-龙虎榜单-机构买卖每日统计"""
@safe_call(cache=True)
def get_lhb_institution_stat(start_date: DateLike, end_date: DateLike) -> pd.DataFrame:
    sd = to_em_date(start_date)
    ed = to_em_date(end_date)
    return ak.stock_lhb_jgmmtj_em(start_date=sd, end_date=ed)

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











