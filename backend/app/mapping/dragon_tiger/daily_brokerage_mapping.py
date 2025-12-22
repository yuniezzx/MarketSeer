"""
每日活跃营业部数据映射模块

提供每日活跃营业部数据的映射功能,支持日期范围查询
"""

from typing import List, Dict, Any
from app.data_sources.client_manager import ClientManager
from .daily_brokerage_config import API_PRIORITY_CONFIG


def map_daily_active_brokerage(
    start_date: str,
    end_date: str,
    client_manager: ClientManager
) -> List[Dict[str, Any]]:
    """
    映射每日活跃营业部数据
    
    Args:
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)
        client_manager: 客户端管理器实例
    
    Returns:
        映射后的数据列表,每个元素为字典格式,包含所有字段
    
    Raises:
        Exception: 当所有API都失败时抛出异常
    """
    last_error = None
    
    # 遍历API优先级配置
    for config in API_PRIORITY_CONFIG:
        try:
            fetch_func = config["fetch_func"]
            result = fetch_func(start_date, end_date, client_manager)
            return result
        except Exception as e:
            last_error = e
            continue
    
    # 如果所有API都失败,抛出异常
    if last_error:
        raise Exception(f"所有API获取每日活跃营业部数据失败: {str(last_error)}")
    
    return []


def map_daily_active_brokerage_by_date(
    date: str,
    client_manager: ClientManager
) -> List[Dict[str, Any]]:
    """
    根据单个日期映射每日活跃营业部数据
    
    这是一个便捷函数,内部调用 map_daily_active_brokerage,
    将 start_date 和 end_date 设置为相同的日期
    
    Args:
        date: 日期 (格式: YYYYMMDD)
        client_manager: 客户端管理器实例
    
    Returns:
        映射后的数据列表,每个元素为字典格式,包含所有字段
    """
    return map_daily_active_brokerage(date, date, client_manager)
