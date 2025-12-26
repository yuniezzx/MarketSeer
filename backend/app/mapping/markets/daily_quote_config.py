"""
每日行情数据映射配置 - API特定函数式架构

每个API都有独立的函数,封装参数转换、API调用、字段映射等所有逻辑
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from logger import logger
from app.data_sources import ClientManager

# ============ API特定函数 ============

def _fetch_from_akshare(
    trade_date: str, client_manager: ClientManager
) -> List[Dict[str, Any]]:
    """
    从 akshare 获取实时行情数据

    特点:
    - API: stock_zh_a_spot_em
    - 参数: 无需参数,获取所有A股实时行情
    - 返回 DataFrame，每行是一只股票的行情数据

    Args:
        trade_date: 交易日期 (格式: YYYYMMDD，如 '20231220')
        client_manager: 客户端管理器

    Returns:
        映射后的行情数据列表
    """
    try:
        # 1. 调用API (实时行情API无需日期参数)
        client = client_manager.get_client("akshare")
        data = client.fetch("stock_zh_a_spot_em", {})

        if data is None or (isinstance(data, pd.DataFrame) and len(data) == 0):
            logger.info(f"未获取到行情数据: {trade_date}")
            return []

        # 2. 字段映射 (根据用户提供的24列数据样本)
        field_mapping = {
            "code": "代码",
            "name": "名称",
            "close": "最新价",
            "change_percent": "涨跌幅",
            "change": "涨跌额",
            "volume": "成交量",
            "amount": "成交额",
            "amplitude": "振幅",
            "high": "最高",
            "low": "最低",
            "open": "今开",
            "pre_close": "昨收",
            "volume_ratio": "量比",
            "turnover_rate": "换手率",
            "pe_ratio_dynamic": "市盈率-动态",
            "pb_ratio": "市净率",
            "total_market_cap": "总市值",
            "circulating_market_cap": "流通市值",
            "rise_speed": "涨速",
            "change_5min": "5分钟涨跌",
            "change_60d": "60日涨跌幅",
            "change_ytd": "年初至今涨跌幅",
        }

        # 3. 转换 DataFrame 为字典列表
        result = []
        for _, row in data.iterrows():
            mapped_item = {}
            
            # 映射字段
            for model_field, api_field in field_mapping.items():
                if api_field in row:
                    value = row[api_field]
                    mapped_item[model_field] = _convert_field_value(model_field, value)
                else:
                    mapped_item[model_field] = _get_default_value(model_field)
            
            # 添加交易日期
            mapped_item["trade_date"] = trade_date
            
            result.append(mapped_item)

        logger.info(f"成功获取行情数据: {len(result)} 条记录")
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
        转换后的值,NaN 值返回 None (数据库中存储为 NULL)
    """
    # 处理 NaN - 返回 None,在数据库中存储为 NULL
    if pd.isna(value):
        return None
    
    # 处理 None
    if value is None:
        return _get_default_value(field_name)

    # 字符串类型字段
    if field_name in ["code", "name", "trade_date"]:
        return str(value).strip() if value else ""

    # 数值类型字段
    else:
        try:
            # 移除百分号(如果有)
            if isinstance(value, str) and "%" in value:
                value = value.replace("%", "")
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
    if field_name in ["code", "name", "trade_date"]:
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
    "trade_date",  # 交易日期
    "open",  # 开盘价
    "close",  # 收盘价
    "high",  # 最高价
    "low",  # 最低价
    "pre_close",  # 昨收价
    "volume",  # 成交量(手)
    "amount",  # 成交额(元)
    "change",  # 涨跌额
    "change_percent",  # 涨跌幅(%)
    "amplitude",  # 振幅(%)
    "turnover_rate",  # 换手率(%)
    "volume_ratio",  # 量比
    "pe_ratio_dynamic",  # 市盈率(动态)
    "pb_ratio",  # 市净率
    "total_market_cap",  # 总市值(亿元)
    "circulating_market_cap",  # 流通市值(亿元)
    "rise_speed",  # 涨速(%)
    "change_5min",  # 5分钟涨跌(%)
    "change_60d",  # 60日涨跌幅(%)
    "change_ytd",  # 年初至今涨跌幅(%)
]

# ============ 配置说明 ============

"""
每日行情映射配置说明

1. 核心特点:
   - 使用实时行情API,获取所有A股数据
   - 返回列表数据,每只股票一条记录
   - 字段映射基于用户提供的24列数据样本

2. API函数签名:
   - trade_date: str - 交易日期 (YYYYMMDD)
   - client_manager: ClientManager - 客户端管理器
   - 返回: List[Dict[str, Any]] - 映射后的行情数据列表

3. 数据类型:
   - 字符串: code, name, trade_date
   - 数值: 其他所有字段 (Float/BigInteger)

4. 数据来源:
   - akshare.stock_zh_a_spot_em() - 东方财富A股实时行情

5. 扩展方式:
   如需添加新数据源:
   - 定义 _fetch_from_xxx 函数
   - 添加到 API_PRIORITY_CONFIG
   - 保持函数签名一致

示例使用:
    from app.mapping.markets.daily_quote_config import API_PRIORITY_CONFIG
    
    for api_config in API_PRIORITY_CONFIG:
        func = api_config['fetch_func']
        result = func(trade_date, client_manager)
"""
