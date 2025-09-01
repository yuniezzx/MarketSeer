"""
pipeline.clients.akshare_client
Akshare 数据源客户端实现（放在 pipeline/clients 下）

职责：
- 实现 DataClient.fetch(endpoint, **params) -> pandas.DataFrame
- 仅负责调用 akshare 并返回原始 DataFrame，不做持久化或复杂 ETL
"""

from typing import Any, Dict, Optional
import logging

import pandas as pd

from .base import DataClient, to_dataframe

logger = logging.getLogger(__name__)

# 延迟导入 akshare 与 tenacity，以避免强制依赖
try:
    import akshare as ak
except Exception:  # pragma: no cover - optional dependency
    ak = None


class AkshareClient(DataClient):
    """最小化 akshare 客户端实现：将 akshare 函数调用封装为 fetch"""

    name = "akshare"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config=config)
        if ak is None:
            logger.warning("akshare 未安装或不可用，调用时会失败")

    def health_check(self) -> bool:
        """简单健康检查：确认 akshare 可用"""
        return ak is not None

    def _call(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def fetch(self, endpoint: str, **params) -> pd.DataFrame:
        """
        通过 akshare 的函数名拉取数据，例如:
            client.fetch("stock_zh_a_daily", symbol="000001.SZ", start_date="20220101")
        注意：akshare 各接口参数名可能不同，请参考 akshare 文档或在 REPL 中 inspect。
        """
        if ak is None:
            raise RuntimeError("akshare 库不可用，请先安装 akshare")

        func = getattr(ak, endpoint, None)
        if func is None:
            raise AttributeError(f"akshare 中未找到接口: {endpoint}")

        try:
            res = self._call(func, **params)
            return to_dataframe(res)
        except Exception:
            logger.exception("调用 akshare 接口失败")
            raise


__all__ = ["AkshareClient"]
