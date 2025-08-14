# -*- coding: utf-8 -*-
"""
仅用于“调用接口获得数据”的轻量封装：
- 不做字段映射、不做清洗转换、不做入库
- 直接返回 AkShare 原始 DataFrame / 数据表
"""

from typing import Literal
import akshare as ak


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