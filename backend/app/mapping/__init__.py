"""
Mapping Layer

负责将不同数据源的原始数据映射到模型字段,并实现字段级别的多源降级机制
"""

from .base_mapper import BaseMapper, StockInfoMapper
from .stock_info_mapping import STOCK_INFO_FIELD_MAPPING, API_CONFIGS

__all__ = [
    'BaseMapper',
    'StockInfoMapper',
    'STOCK_INFO_FIELD_MAPPING',
    'API_CONFIGS',
]
