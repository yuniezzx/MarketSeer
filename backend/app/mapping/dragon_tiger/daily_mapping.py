"""
龙虎榜数据映射 - API特定函数式架构

提供 map_daily_dragon_tiger 主函数,获取指定日期范围的龙虎榜数据
"""

from typing import List, Dict, Any
from logger import logger
from app.data_sources import ClientManager
from .daily_config import API_PRIORITY_CONFIG


def map_daily_dragon_tiger(
    start_date: str, end_date: str, client_manager: ClientManager
) -> List[Dict[str, Any]]:
    """
    映射龙虎榜数据 - 主函数

    获取指定日期范围的龙虎榜数据并进行字段映射

    Args:
        start_date: 开始日期 (格式: YYYYMMDD，如 '20231220')
        end_date: 结束日期 (格式: YYYYMMDD)
        client_manager: 客户端管理器

    Returns:
        映射后的龙虎榜数据列表，每个元素是一条龙虎榜记录
    """
    logger.info(f"开始获取龙虎榜数据: {start_date} - {end_date}")

    result = []

    # 按优先级遍历 API 配置
    for api_config in API_PRIORITY_CONFIG:
        api_name = api_config["name"]
        fetch_func = api_config["fetch_func"]

        logger.info(f"尝试 API: {api_name} (优先级 {api_config['priority']})")

        try:
            # 调用 API 特定函数
            data = fetch_func(start_date, end_date, client_manager)

            if data:
                result = data
                logger.info(f"API {api_name} 成功获取 {len(data)} 条龙虎榜记录")
                # 获取到数据后停止降级
                break
            else:
                logger.warning(f"API {api_name} 未获取到数据")

        except Exception as e:
            logger.error(f"API {api_name} 执行失败: {e}")
            continue

    # 最终结果检查
    if not result:
        logger.warning(f"未能获取到龙虎榜数据: {start_date} - {end_date}")
    else:
        logger.info(f"龙虎榜数据映射完成: 共 {len(result)} 条记录")

    return result


def map_daily_dragon_tiger_by_date(
    date: str, client_manager: ClientManager
) -> List[Dict[str, Any]]:
    """
    获取指定单日的龙虎榜数据（便捷方法）

    Args:
        date: 日期 (格式: YYYYMMDD，如 '20231220')
        client_manager: 客户端管理器

    Returns:
        映射后的龙虎榜数据列表
    """
    return map_daily_dragon_tiger(date, date, client_manager)
