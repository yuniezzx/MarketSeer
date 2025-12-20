"""
龙虎榜数据映射配置 - API特定函数式架构

每个API都有独立的函数,封装参数转换、API调用、字段映射等所有逻辑
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from logger import logger
from app.data_sources import ClientManager

# ============ API特定函数 ============


def _fetch_from_akshare(
    start_date: str, end_date: str, client_manager: ClientManager
) -> List[Dict[str, Any]]:
    """
    从 akshare 获取龙虎榜数据

    特点:
    - API: stock_lhb_detail_em
    - 参数格式: {'start_date': 'YYYYMMDD', 'end_date': 'YYYYMMDD'}
    - 返回 DataFrame，每行是一个上榜股票

    Args:
        start_date: 开始日期 (格式: YYYYMMDD，如 '20231220')
        end_date: 结束日期 (格式: YYYYMMDD)
        client_manager: 客户端管理器

    Returns:
        映射后的龙虎榜数据列表
    """
    try:
        # 1. 调用API
        client = client_manager.get_client("akshare")
        data = client.fetch("stock_lhb_detail_em", {"start_date": start_date, "end_date": end_date})

        if data is None or (isinstance(data, pd.DataFrame) and len(data) == 0):
            logger.info(f"未获取到龙虎榜数据: {start_date} - {end_date}")
            return []

        # 2. 字段映射
        field_mapping = {
            "code": "代码",
            "name": "名称",
            "listed_date": "上榜日",
            "close_price": "收盘价",
            "change_percent": "涨跌幅",
            "turnover_rate": "换手率",
            "circulating_market_cap": "流通市值",
            "lhb_buy_amount": "龙虎榜买入额",
            "lhb_sell_amount": "龙虎榜卖出额",
            "lhb_net_amount": "龙虎榜净买额",
            "lhb_trade_amount": "龙虎榜成交额",
            "market_total_amount": "市场总成交额",
            "lhb_net_ratio": "净买额占总成交比",
            "lhb_trade_ratio": "成交额占总成交比",
            "analysis": "解读",
            "reasons": "上榜原因",
        }

        # 3. 转换 DataFrame 为字典列表
        result = []
        for _, row in data.iterrows():
            mapped_item = {}
            for model_field, api_field in field_mapping.items():
                if api_field in row:
                    value = row[api_field]
                    # 数据类型转换
                    mapped_item[model_field] = _convert_field_value(model_field, value)
                else:
                    # 字段缺失，设置默认值
                    mapped_item[model_field] = _get_default_value(model_field)

            result.append(mapped_item)

        logger.info(f"成功获取龙虎榜数据: {len(result)} 条记录")
        return result

    except Exception as e:
        logger.error(f"_fetch_from_akshare 失败: {e}")
        return []


def _convert_field_value(field_name: str, value: Any) -> Any:
    """
    根据字段类型转换值

    Args:
        field_name: 字段名
        value: 原始值

    Returns:
        转换后的值
    """
    # 处理 NaN 和 None
    if pd.isna(value) or value is None:
        return _get_default_value(field_name)

    # 字符串类型字段
    if field_name in ["code", "name", "analysis", "reasons"]:
        return str(value) if value else ""

    # 日期类型字段
    elif field_name == "listed_date":
        # 保持原始格式或转换为字符串
        return str(value) if value else ""

    # 数值类型字段
    else:
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0


def _get_default_value(field_name: str) -> Any:
    """
    获取字段的默认值

    Args:
        field_name: 字段名

    Returns:
        默认值
    """
    if field_name in ["code", "name", "analysis", "reasons", "listed_date"]:
        return ""
    else:
        return 0.0


# ============ 简化配置 ============

# API优先级配置
API_PRIORITY_CONFIG = [
    {"priority": 1, "name": "akshare", "fetch_func": _fetch_from_akshare},
]

# 所有支持的字段列表
ALL_FIELDS = [
    "code",  # 股票代码
    "name",  # 股票名称
    "listed_date",  # 上榜日期
    "close_price",  # 收盘价
    "change_percent",  # 涨跌幅
    "turnover_rate",  # 换手率
    "circulating_market_cap",  # 流通市值
    "lhb_buy_amount",  # 龙虎榜买入额
    "lhb_sell_amount",  # 龙虎榜卖出额
    "lhb_net_amount",  # 龙虎榜净买额
    "lhb_trade_amount",  # 龙虎榜成交额
    "market_total_amount",  # 市场总成交额
    "lhb_net_ratio",  # 龙虎榜净买额占总成交比
    "lhb_trade_ratio",  # 龙虎榜成交额占总成交比
    "analysis",  # 解读
    "reasons",  # 上榜原因
]

# ============ 配置说明 ============

"""
龙虎榜映射配置说明

1. 核心特点:
   - 使用日期范围查询，而非单个股票代码
   - 返回列表数据，一天可能有多只股票上榜
   - 字段映射基于用户提供的 LHB_FIELD_MAPPING

2. API函数签名:
   - start_date: str - 开始日期 (YYYYMMDD)
   - end_date: str - 结束日期 (YYYYMMDD)
   - client_manager: ClientManager - 客户端管理器
   - 返回: List[Dict[str, Any]] - 映射后的龙虎榜数据列表

3. 数据类型:
   - 字符串: code, name, analysis, reasons
   - 日期: listed_date
   - 数值: 其他所有字段 (Float)

4. 扩展方式:
   如需添加新数据源:
   - 定义 _fetch_from_xxx 函数
   - 添加到 API_PRIORITY_CONFIG
   - 保持函数签名一致

示例使用:
    from app.mapping.dragon_tiger.daily_config import API_PRIORITY_CONFIG
    
    for api_config in API_PRIORITY_CONFIG:
        func = api_config['fetch_func']
        result = func(start_date, end_date, client_manager)
"""
