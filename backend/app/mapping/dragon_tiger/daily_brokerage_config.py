"""每日活跃营业部数据映射配置"""

from typing import Any, Dict, List, Optional
import pandas as pd
from app.data_sources.client_manager import ClientManager


def _fetch_from_akshare(
    start_date: str, end_date: str, client_manager: ClientManager
) -> List[Dict[str, Any]]:
    """
    从 akshare 获取每日活跃营业部数据
    API: stock_lhb_hyyyb_em

    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        client_manager: 客户端管理器

    Returns:
        List[Dict]: 营业部数据列表
    """
    akshare_client = client_manager.get_client("akshare")

    # 调用 akshare API
    df = akshare_client.fetch(
        "stock_lhb_hyyyb_em", params={"start_date": start_date, "end_date": end_date}
    )

    if df is None or df.empty:
        return []

    # 字段映射
    field_mapping = {
        "brokerage_code": "营业部代码",
        "brokerage_name": "营业部名称",
        "listed_date": "上榜日",
        "buy_stock_count": "买入个股数",
        "sell_stock_count": "卖出个股数",
        "buy_total_amount": "买入总金额",
        "sell_total_amount": "卖出总金额",
        "net_total_amount": "总买卖净额",
        "buy_stocks": "买入股票",
    }

    result = []
    for _, row in df.iterrows():
        record = {}
        for model_field, api_field in field_mapping.items():
            value = row.get(api_field)

            # 处理 NaN 和空值
            if pd.isna(value) or value == "" or value is None:
                record[model_field] = _get_default_value(model_field)
            else:
                record[model_field] = _convert_field_value(model_field, value)

        result.append(record)

    return result


def _convert_field_value(field_name: str, value: Any) -> Any:
    """
    转换字段值为适当的类型

    Args:
        field_name: 字段名
        value: 原始值

    Returns:
        转换后的值
    """
    # String 类型字段
    if field_name in ["brokerage_code", "brokerage_name", "listed_date", "buy_stocks"]:
        return str(value).strip() if value else None

    # Integer 类型字段
    elif field_name in ["buy_stock_count", "sell_stock_count"]:
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None

    # Float 类型字段
    elif field_name in ["buy_total_amount", "sell_total_amount", "net_total_amount"]:
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None

    return value


def _get_default_value(field_name: str) -> Any:
    """
    获取字段的默认值

    Args:
        field_name: 字段名

    Returns:
        默认值
    """
    # 数值类型返回 None，字符串类型返回 None
    return None


# API 优先级配置
API_PRIORITY_CONFIG = [
    {
        "priority": 1,
        "name": "akshare",
        "fetch_func": _fetch_from_akshare,
    }
]

# 所有字段列表
ALL_FIELDS = [
    "brokerage_code",
    "brokerage_name",
    "listed_date",
    "buy_stock_count",
    "sell_stock_count",
    "buy_total_amount",
    "sell_total_amount",
    "net_total_amount",
    "buy_stocks",
]
