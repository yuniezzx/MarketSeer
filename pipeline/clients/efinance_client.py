"""
pipeline.clients.efinance_client
Efinance 数据源客户端实现（放在 pipeline/clients 下）

职责：
- 实现 DataClient.fetch(endpoint, **params) -> pandas.DataFrame
- 仅负责调用 efinance 并返回原始 DataFrame
- 与 AkshareClient 保持相同接口，以便互换使用
"""

from typing import Any, Dict, Optional
import logging

import pandas as pd

from .base import DataClient, to_dataframe

logger = logging.getLogger(__name__)

# 延迟导入 efinance 与 tenacity，以避免强制依赖
try:
    import efinance as ef
except Exception:  # pragma: no cover - optional dependency
    ef = None


class EfinanceClient(DataClient):
    """最小化 efinance 客户端实现：将 efinance 的调用封装为 fetch"""

    name = "efinance"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config=config)
        if ef is None:
            logger.warning("efinance 未安装或不可用，调用时会失败")

    def health_check(self) -> bool:
        """简单健康检查：确认 efinance 可用"""
        return ef is not None

    def _call(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def fetch(self, endpoint: str, **params) -> pd.DataFrame:
        """
        通过 efinance 的函数名拉取数据。例如：
            client.fetch("stock.get_quote", code="000001")
        注意：efinance 的 API 组织可能与 akshare 不同，endpoint 可以是顶级函数名或点分路径（示例中支持点分路径）。
        """
        if ef is None:
            raise RuntimeError("efinance 库不可用，请先安装 efinance")

        # 支持 "module.func" 点分路径，比如 "stock.get_quote"
        func = None
        if "." in endpoint:
            parts = endpoint.split(".")
            module = ef
            for p in parts[:-1]:
                module = getattr(module, p, None)
                if module is None:
                    break
            if module is not None:
                func = getattr(module, parts[-1], None)
        else:
            func = getattr(ef, endpoint, None)

        if func is None:
            raise AttributeError(f"efinance 中未找到接口: {endpoint}")

        try:
            res = self._call(func, **params)
            return to_dataframe(res)
        except Exception:
            logger.exception("调用 efinance 接口失败")
            raise


__all__ = ["EfinanceClient"]
