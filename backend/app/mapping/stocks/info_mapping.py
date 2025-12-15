"""
股票基础信息映射 - API特定函数式架构

提供 map_stock_info 主函数,实现API级降级机制
核心逻辑:按优先级调用各API特定函数,增量合并结果
"""

from typing import Dict, Any, Set
from logger import logger
from app.data_sources import ClientManager
from .info_config import API_PRIORITY_CONFIG, ALL_FIELDS
from app.utils import add_market_prefix


def map_stock_info(symbol: str, client_manager: ClientManager) -> Dict[str, Any]:
    """
    映射股票基础信息 - 主函数

    实现 API 级降级机制:
    1. 按优先级顺序调用各 API 特定函数
    2. 每个 API 函数内部封装所有逻辑(参数转换、调用、字段提取)
    3. 增量合并结果,不覆盖已有值
    4. 所有字段完整后停止降级

    Args:
        symbol: 股票代码 (如 '002156')
        client_manager: 客户端管理器

    Returns:
        映射后的字段字典
    """
    result = {}
    missing_fields = set(ALL_FIELDS)

    result = _add_computed_fields(result, symbol)

    # 按优先级遍历 API 配置
    for api_config in API_PRIORITY_CONFIG:
        # 检查是否所有字段已完整
        if not missing_fields:
            logger.info(f"[{symbol}] 所有字段已完整,停止降级")
            break

        api_name = api_config['name']
        fetch_func = api_config['fetch_func']

        logger.info(
            f"[{symbol}] 尝试 API: {api_name} "
            f"(优先级 {api_config['priority']}), "
            f"缺失字段数: {len(missing_fields)}"
        )

        # 调用 API 特定函数
        try:
            extracted = fetch_func(symbol, client_manager, missing_fields)

            if extracted:
                # 增量合并结果
                _merge_fields(result, extracted, missing_fields)
                logger.info(f"[{symbol}] API {api_name} 成功提取 {len(extracted)} 个字段")
            else:
                logger.warning(f"[{symbol}] API {api_name} 未提取到任何字段")

        except Exception as e:
            logger.error(f"[{symbol}] API {api_name} 执行失败: {e}")
            continue

    # 最终结果检查
    if missing_fields:
        logger.warning(f"[{symbol}] 映射完成,仍有 {len(missing_fields)} 个字段缺失: " f"{missing_fields}")
    else:
        logger.info(f"[{symbol}] 映射完成,所有字段完整")

    return result


def _merge_fields(result: Dict[str, Any], new_fields: Dict[str, Any], missing_fields: Set[str]) -> None:
    """
    增量合并字段(不覆盖已有值)

    Args:
        result: 结果字典(会被修改)
        new_fields: 新提取的字段
        missing_fields: 缺失字段集合(会被修改)
    """
    for field, value in new_fields.items():
        if field not in result:
            result[field] = value
            missing_fields.discard(field)


def _add_computed_fields(result: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    """添加计算和默认字段"""
    # 1. 从代码计算 market
    if 'market' not in result:
        result['market'] = add_market_prefix(symbol)

    # 2. 设置默认 status
    if 'status' not in result:
        result['status'] = '上市'

    # 3. 设置默认 tracking
    if 'tracking' not in result:
        result['tracking'] = False

    return result
