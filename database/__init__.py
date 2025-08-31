"""
数据库操作模块

此模块包含数据库相关功能：
- connection: 数据库连接管理
- operations: 数据库操作封装
- migrations: 数据库迁移脚本
"""

from .connection import DatabaseManager
from .operations import DatabaseOperations

__all__ = ['DatabaseManager', 'DatabaseOperations']
