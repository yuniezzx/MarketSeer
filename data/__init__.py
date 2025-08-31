"""
数据获取模块

此模块包含数据获取相关的功能：
- akshare_client: akshare数据接口封装
- data_fetcher: 通用数据获取器
- validators: 数据验证器
"""

from .akshare_client import AkshareClient

# Optional imports for backward compatibility; ignore if modules are missing
try:
    from .data_fetcher import DataFetcher  # type: ignore
except Exception:
    DataFetcher = None  # type: ignore

try:
    from .validators import DataValidator  # type: ignore
except Exception:
    DataValidator = None  # type: ignore

__all__ = ['AkshareClient']
