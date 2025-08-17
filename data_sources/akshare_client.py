from typing import Literal, Union, Any, Callable
from datetime import date, datetime
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

# === 工具函数 ===

def _detect_market_prefix(stock_code: str) -> Literal["SH", "SZ"]:
    """
    XQ 接口需要带市场前缀：
    - 600/601/603/605/688 -> SH
    - 其余常见 A 股代码 -> SZ
    """
    code = stock_code.strip()
    if code.startswith(("600", "601", "603", "605", "688")):
        return "SH"
    return "SZ"


# === 现货行情 ===

def get_sh_a_spot():
    """
    上证 A 股现货行情
    对应：ak.stock_sh_a_spot_em()
    返回：pandas.DataFrame（原始列）
    """
    return ak.stock_sh_a_spot_em()


def get_zh_a_spot():
    """
    A 股（沪深）整体现货行情
    对应：ak.stock_zh_a_spot_em()
    返回：pandas.DataFrame（原始列）
    """
    return ak.stock_zh_a_spot_em()


# === 基础资料（直接返回原始 DF） ===

def get_profile_em(stock_code: str):
    """
    东方财富-个股基础信息（item/value 结构）
    对应：ak.stock_individual_info_em(symbol=xxx)
    参数：
        stock_code: 6 位股票代码（不带市场前缀），如 '600000'
    返回：pandas.DataFrame（原始列）
    """
    return ak.stock_individual_info_em(symbol=stock_code)


def get_profile_xq(stock_code: str):
    """
    雪球-个股基础信息（AkShare 封装）
    对应：ak.stock_individual_basic_info_xq(symbol='SH600000' / 'SZ000001')
    参数：
        stock_code: 6 位股票代码（不带市场前缀），自动拼接 SH/SZ
    返回：pandas.DataFrame（原始列）
    """
    market = _detect_market_prefix(stock_code)
    symbol = f"{market}{stock_code}"
    return ak.stock_individual_basic_info_xq(symbol)


# === 龙虎榜 ===

def get_lhb_detail(date: str, stock_code: str):
    """
    东方财富网-数据中心-龙虎榜单-龙虎榜详情
    对应：ak.stock_lhb_detail_em(date='YYYYMMDD', symbol='600000')
    参数：
        date: 交易日，格式 'YYYYMMDD'，如 '20250115'
        stock_code: 6 位股票代码（不带市场前缀），如 '600000'
    返回：
        pandas.DataFrame（原始列，包含买入/卖出席位明细）
    """
    return ak.stock_lhb_detail_em(date=date, symbol=stock_code)


def get_lhb_stock_statistic(stock_code: str) -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-个股上榜统计
    对应：ak.stock_lhb_stock_statistic_em(symbol='600000')
    参数：
        stock_code: 6 位股票代码（不带市场前缀），如 '600000'
    返回：
        pandas.DataFrame（原始列，包含该股票历次上榜统计信息）
    """
    return ak.stock_lhb_stock_statistic_em(symbol=stock_code)


def get_lhb_institution_stat() -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-机构买卖每日统计
    对应: ak.stock_lhb_jgmmtj_em()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lhb_jgmmtj_em()


def get_lhb_institution_tracking() -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-机构席位追踪
    对应: ak.stock_lhb_jgstatistic_em()

    参数:
        无

    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lhb_jgstatistic_em()


def get_lhb_active_broker() -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-每日活跃营业部
    对应: ak.stock_lhb_hyyyb_em()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lhb_hyyyb_em()


def get_lhb_broker_detail(broker_code: str) -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-营业部历史交易明细-营业部交易明细
    对应: ak.stock_lhb_yyb_detail_em(symbol='营业部代码')
    参数:
        broker_code: 营业部代码，如 '10188715'
    返回:
        pandas.DataFrame（原始列，单次返回该营业部的所有历史数据）
    """
    return ak.stock_lhb_yyb_detail_em(symbol=broker_code)


def get_lhb_broker_rank() -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-营业部排行
    对应: ak.stock_lhb_yybph_em()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lhb_yybph_em()


def get_lhb_broker_statistic() -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-营业部统计
    对应: ak.stock_lhb_traderstatistic_em()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lhb_traderstatistic_em()


def get_lhb_stock_detail(stock_code: str) -> pd.DataFrame:
    """
    东方财富网-数据中心-龙虎榜单-个股龙虎榜详情
    对应: ak.stock_lhb_stock_detail_em(symbol='600077')
    参数:
        stock_code: 股票代码（6 位，不带市场前缀），如 '600077'
    返回:
        pandas.DataFrame（原始列，单次返回该股票的所有历史龙虎榜详情数据）
    """
    return ak.stock_lhb_stock_detail_em(symbol=stock_code)


def get_lhb_broker_most() -> pd.DataFrame:
    """
    同花顺-龙虎榜-营业部排行-上榜次数最多
    对应: ak.stock_lh_yyb_most()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lh_yyb_most()


def get_lhb_broker_capital() -> pd.DataFrame:
    """
    同花顺-龙虎榜-营业部排行-资金实力最强
    目标地址: https://data.10jqka.com.cn/market/longhu/
    对应: ak.stock_lh_yyb_capital()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lh_yyb_capital()


def get_lhb_broker_control() -> pd.DataFrame:
    """
    同花顺-龙虎榜-营业部排行-抱团操作实力
    对应: ak.stock_lh_yyb_control()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史数据）
    """
    return ak.stock_lh_yyb_control()


def get_lhb_detail_daily_sina(date: str) -> pd.DataFrame:
    """
    新浪财经-龙虎榜-每日详情
    对应: ak.stock_lhb_detail_daily_sina(date='YYYY-MM-DD')
    参数:
        date: 交易日，格式 'YYYY-MM-DD'，如 '2025-01-15'
    返回:
        pandas.DataFrame（原始列，单次返回指定日期的所有数据）
    """
    return ak.stock_lhb_detail_daily_sina(date=date)


def get_lhb_stock_statistic_sina(symbol: str) -> pd.DataFrame:
    """
    新浪财经-龙虎榜-个股上榜统计
    对应: ak.stock_lhb_ggtj_sina(symbol='600000')
    参数:
        symbol: 股票代码（6 位，不带市场前缀），如 '600000'
    返回:
        pandas.DataFrame（原始列，单次返回该股票的所有历史上榜统计数据）
    """
    return ak.stock_lhb_ggtj_sina(symbol=symbol)


def get_lhb_broker_statistic_sina(symbol: str) -> pd.DataFrame:
    """
    新浪财经-龙虎榜-营业部上榜统计
    对应: ak.stock_lhb_yytj_sina(symbol='营业部代码')
    参数:
        symbol: 营业部代码，如 'sz000001' 或 'sh600000' 对应的营业部代号（需按 AkShare 要求传入）
    返回:
        pandas.DataFrame（原始列，单次返回该营业部的所有历史上榜统计数据）
    """
    return ak.stock_lhb_yytj_sina(symbol=symbol)


def get_lhb_institution_tracking_sina(symbol: str) -> pd.DataFrame:
    """
    新浪财经-龙虎榜-机构席位追踪
    对应: ak.stock_lhb_jgzz_sina(symbol='600000')
    参数:
        symbol: 股票代码（6 位，不带市场前缀），如 '600000'
    返回:
        pandas.DataFrame（原始列，单次返回该股票的所有历史机构席位追踪数据）
    """
    return ak.stock_lhb_jgzz_sina(symbol=symbol)


def get_lhb_institution_detail_sina() -> pd.DataFrame:
    """
    新浪财经-龙虎榜-机构席位成交明细
    对应: ak.stock_lhb_jgmx_sina()
    参数:
        无
    返回:
        pandas.DataFrame（原始列，单次返回所有历史机构席位成交明细数据）
    """
    return ak.stock_lhb_jgmx_sina()

