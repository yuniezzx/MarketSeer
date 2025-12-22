"""
股票基础信息映射配置 - API特定函数式架构

每个API都有独立的函数,封装参数转换、API调用、字段映射等所有逻辑
"""

from typing import Dict, Any, Set, Optional, Callable
import pandas as pd
from logger import logger
from app.utils import add_market_prefix
from app.data_sources import ClientManager

# ============ API特定函数 ============


def _fetch_from_em(
    symbol: str, client_manager: ClientManager, needed_fields: Set[str]
) -> Dict[str, Any]:
    """
    从东方财富获取数据

    特点:
    - 参数格式: 002156 (无前缀)
    - 字段最全
    - 优先级最高

    Args:
        symbol: 股票代码 (如 '002156')
        client_manager: 客户端管理器
        needed_fields: 需要获取的字段集合

    Returns:
        提取到的字段字典
    """
    try:
        # 1. 调用API
        client = client_manager.get_client("akshare")
        data = client.fetch("stock_individual_info_em", {"symbol": symbol})

        if data is None or (isinstance(data, pd.DataFrame) and len(data) == 0):
            return {}

        # 2. 字段映射
        field_mapping = {
            "code": "股票代码",
            "name": "股票简称",
            "full_name": "股票名称",
            "market": "市场类型",
            "industry_code": "行业代码",
            "industry": "行业",
            "establish_date": "成立日期",
            "list_date": "上市日期",
            "main_operation_business": "主营业务",
            "operating_scope": "经营范围",
            "status": "上市状态",
        }

        # 3. 提取需要的字段
        result = {}
        for model_field in needed_fields:
            if model_field in field_mapping:
                api_field = field_mapping[model_field]
                value = _get_value(data, api_field)
                if value is not None and value != "":
                    result[model_field] = value

        print("result:", result)
        return result

    except Exception as e:
        logger.error(f"_fetch_from_em 失败: {e}")
        return {}


def _fetch_from_xq(
    symbol: str, client_manager: ClientManager, needed_fields: Set[str]
) -> Dict[str, Any]:
    """
    从雪球获取数据

    特点:
    - 参数格式: SZ002156 (需要添加市场前缀)
    - 补充东财缺失的字段
    - 返回格式: item-value DataFrame (和东方财富一样)

    Args:
        symbol: 股票代码 (如 '002156')
        client_manager: 客户端管理器
        needed_fields: 需要获取的字段集合

    Returns:
        提取到的字段字典
    """
    try:
        # 1. 参数转换
        xq_symbol = add_market_prefix(symbol)

        # 2. 调用API
        client = client_manager.get_client("akshare")
        data = client.fetch("stock_individual_basic_info_xq", {"symbol": xq_symbol})

        if data is None or (isinstance(data, pd.DataFrame) and len(data) == 0):
            return {}

        # 3. 字段映射 (雪球API的实际字段名)
        field_mapping = {
            "name": "org_short_name_cn",  # 股票简称
            "full_name": "org_name_cn",  # 公司全称
            "establish_date": "established_date",  # 成立日期 (时间戳)
            "list_date": "listed_date",  # 上市日期 (时间戳)
            "main_operation_business": "main_operation_business",  # 主营业务
            "operating_scope": "operating_scope",  # 经营范围
        }

        # 4. 提取需要的字段
        result = {}
        for model_field in needed_fields:
            if model_field in field_mapping:
                api_field = field_mapping[model_field]
                value = _get_value(data, api_field)
                if value is not None and value != "":
                    result[model_field] = value

        # 5. 特殊处理: 行业信息 (嵌套在 affiliate_industry 中)
        if "industry" in needed_fields or "industry_code" in needed_fields:
            industry_data = _get_value(data, "affiliate_industry")
            if industry_data and isinstance(industry_data, dict):
                if "industry" in needed_fields:
                    ind_name = industry_data.get("ind_name")
                    if ind_name:
                        result["industry"] = ind_name
                if "industry_code" in needed_fields:
                    ind_code = industry_data.get("ind_code")
                    if ind_code:
                        result["industry_code"] = ind_code

        return result

    except Exception as e:
        logger.error(f"_fetch_from_xq 失败: {e}")
        return {}


def _fetch_from_efinance(
    symbol: str, client_manager: ClientManager, needed_fields: Set[str]
) -> Dict[str, Any]:
    """
    从 efinance 获取数据

    特点:
    - 参数格式: 002156 (无前缀)
    - 兜底数据源
    - 字段较少

    Args:
        symbol: 股票代码 (如 '002156')
        client_manager: 客户端管理器
        needed_fields: 需要获取的字段集合

    Returns:
        提取到的字段字典
    """
    try:
        # 1. 调用API
        client = client_manager.get_client("efinance")
        data = client.fetch("stock_individual_info", {"stock_codes": symbol})

        if data is None or (isinstance(data, pd.DataFrame) and len(data) == 0):
            return {}

        # 2. 字段映射
        field_mapping = {
            "code": "股票代码",
            "name": "股票简称",
            "full_name": "股票名称",
            "market": "市场",
            "industry": "行业",
            "list_date": "上市日期",
            "status": "上市状态",
        }

        # 3. 提取需要的字段
        result = {}
        for model_field in needed_fields:
            if model_field in field_mapping:
                api_field = field_mapping[model_field]
                value = _get_value(data, api_field)
                if value is not None and value != "":
                    result[model_field] = value

        return result

    except Exception as e:
        logger.error(f"_fetch_from_efinance 失败: {e}")
        return {}


# ============ 辅助函数 ============


def _get_value(data: Any, field: str) -> Optional[Any]:
    """
    从DataFrame或dict中提取值

    Args:
        data: 数据源 (DataFrame 或 dict)
        field: 字段名

    Returns:
        提取到的值,失败返回 None
    """
    try:
        if isinstance(data, pd.DataFrame):
            if "item" in data.columns and "value" in data.columns:
                matched_rows = data[data["item"] == field]
                if not matched_rows.empty:
                    value = matched_rows.iloc[0]["value"]
                    if pd.isna(value):
                        return None
                    return value
            elif field in data.columns:
                value = data.iloc[0][field]
                if pd.isna(value):
                    return None
                return value
        elif isinstance(data, dict):
            return data.get(field)
        return None
    except Exception:
        return None


# ============ 简化配置 ============

# API优先级配置: 每个API只需配置优先级、名称和对应的函数
API_PRIORITY_CONFIG = [
    {"priority": 1, "name": "em", "fetch_func": _fetch_from_em},
    {"priority": 2, "name": "xq", "fetch_func": _fetch_from_xq},
    {"priority": 3, "name": "efinance", "fetch_func": _fetch_from_efinance},
]

# 所有支持的字段列表
ALL_FIELDS = [
    "code",  # 股票代码
    "name",  # 股票简称
    "full_name",  # 股票全称
    # 'market',  # 市场类型
    "industry_code",  # 行业代码
    "industry",  # 行业名称
    "establish_date",  # 成立日期
    "list_date",  # 上市日期
    "main_operation_business",  # 主营业务
    "operating_scope",  # 经营范围
    # 'status',  # 上市状态
    # 'tracking', # 是否跟踪
]

# ============ 配置说明 ============

"""
API特定函数式架构设计说明

1. 核心理念:
   - 每个API都有独立的函数 (如 _fetch_from_em, _fetch_from_xq)
   - 函数内部封装所有逻辑: 参数转换、API调用、字段映射
   - 配置只保留最简信息: 优先级、名称、函数引用

2. 函数签名:
   所有API函数都遵循统一签名:
   - symbol: str - 股票代码
   - client_manager: ClientManager - 客户端管理器
   - needed_fields: Set[str] - 需要获取的字段集合
   - 返回: Dict[str, Any] - 提取到的字段字典

3. 工作流程:
   - 主函数按优先级遍历配置
   - 调用对应的API函数
   - API函数内部处理所有细节
   - 返回提取到的字段
   - 主函数增量合并结果

4. 扩展方式:
   添加新API三步走:
   - 第1步: 定义 _fetch_from_xxx 函数
   - 第2步: 在 API_PRIORITY_CONFIG 中添加配置
   - 第3步: 完成!

5. 与之前方案的区别:
   - 之前: 通用函数 + 复杂配置 (本质是OOP换位置)
   - 现在: 专用函数 + 极简配置 (真正的函数式)
   - 优势: 每个API的逻辑一目了然,无需跨文件查看

示例使用:
    from app.mapping.stocks.config import API_PRIORITY_CONFIG
    
    # 遍历配置
    for api_config in API_PRIORITY_CONFIG:
        name = api_config['name']  # 'em', 'xq', 'efinance'
        func = api_config['fetch_func']  # 对应的函数
        
        # 调用API函数
        result = func(symbol, client_manager, needed_fields)
"""
