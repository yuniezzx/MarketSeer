"""
DB 交互模块
"""

from .stocks.info import StockInfoRepository
from .dragon_tiger.daily_dragon_tiger import DailyDragonTigerRepository

__all__ = ["StockInfoRepository", "DailyDragonTigerRepository"]
