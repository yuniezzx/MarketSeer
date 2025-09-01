"""
pipeline.clients.base
统一数据源客户端抽象基类（放在 pipeline/clients 下）

职责：
- 定义 DataClient 接口：fetch(endpoint, **params) -> pandas.DataFrame
- 提供可复用的轻量工具（可选）
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class DataClient(ABC):
    """
    统一数据源客户端接口：返回 pandas.DataFrame

    说明：
    - `endpoint` 是数据源内部的标识（例如 akshare 的函数名）
    - client 实现只负责拉取并返回原始 DataFrame，不负责持久化或复杂 ETL
    """

    name: str = "base"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def fetch(self, endpoint: str, **params) -> pd.DataFrame:
        """
        拉取指定 endpoint 的原始数据，返回 pandas.DataFrame。
        子类必须实现此方法。
        """
        raise NotImplementedError

    def health_check(self) -> bool:
        """可选的健康检查方法，默认返回 True（子类可覆盖）"""
        return True


def to_dataframe(value: Any) -> pd.DataFrame:
    """辅助：尽量把返回值转换为 DataFrame（若无法转换返回空 DataFrame）"""
    if isinstance(value, pd.DataFrame):
        return value
    try:
        return pd.DataFrame(value)
    except Exception:
        # 避免在基础库依赖 logger 配置，保持简单
        return pd.DataFrame()
