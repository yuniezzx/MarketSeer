"""
Mapping Layer

负责将不同数据源的原始数据映射到模型字段,并实现API级别的多源降级机制
"""

from .stocks.info_mapping import map_stock_info

__all__ = ['map_stock_info']
