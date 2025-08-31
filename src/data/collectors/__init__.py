"""
数据收集模块

提供统一的数据收集接口，支持多种数据源：
- Tushare: 中国A股数据
- AKShare: 多源金融数据
- yfinance: 全球股票数据
"""

from .base_collector import BaseCollector
from .data_types import (
    StockInfo,
    HistoricalData,
    RealtimeData,
    FinancialData,
    DataCollectorConfig,
)
from .exceptions import (
    DataCollectorError,
    APIError,
    RateLimitError,
    DataQualityError,
    AuthenticationError,
    SymbolNotFoundError,
    DataNotAvailableError,
    ValidationError,
    NetworkError,
    ConfigurationError,
    RetryExhaustedError,
    DataParsingError,
)


# 延迟导入具体的收集器以避免循环依赖
def get_tushare_collector():
    """获取Tushare数据收集器"""
    from .tushare_collector import TushareCollector

    return TushareCollector


def get_akshare_collector():
    """获取AKShare数据收集器"""
    from .akshare_collector import AKShareCollector

    return AKShareCollector


def get_yfinance_collector():
    """获取yfinance数据收集器"""
    from .yfinance_collector import YFinanceCollector

    return YFinanceCollector


__all__ = [
    'BaseCollector',
    'StockInfo',
    'HistoricalData',
    'RealtimeData',
    'FinancialData',
    'DataCollectorConfig',
    'DataCollectorError',
    'APIError',
    'RateLimitError',
    'DataQualityError',
    'AuthenticationError',
    'SymbolNotFoundError',
    'DataNotAvailableError',
    'ValidationError',
    'NetworkError',
    'ConfigurationError',
    'RetryExhaustedError',
    'DataParsingError',
    'get_tushare_collector',
    'get_akshare_collector',
    'get_yfinance_collector',
]
