"""
数据库模型模块

该模块包含所有数据库模型类，按业务领域组织：
- base: 基础模型类和数据库实例
- stock: 股票相关模型（基本信息、日线数据、分钟数据）
- market: 市场相关模型（指数信息、板块信息）
"""

from .base import db, init_db, BaseModel

# 导入股票相关模型
from .stock import StockInfo, StockDaily, StockMinute

# 导入市场相关模型
from .market import IndexInfo, SectorInfo

# 定义公开接口
__all__ = [
    # 基础设施
    'db',
    'init_db',
    'BaseModel',

    # 股票模型
    'StockInfo',

    # 市场模型
    'IndexInfo',
    'SectorInfo',
]
