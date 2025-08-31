# Efinance client wrapper with stock_info mapping
# Provides:
# - stock_individual_info_ef -> returns raw efinance.get_base_info result (no mapping)
# - stock_individual_basic_info_ef -> alias for the same
#
# This file originally included a best-effort mapping function. Per request,
# stock_individual_info_ef will now directly return efinance's original result
# without filtering or mapping.

from typing import Any, Optional, Dict, List, Union
import datetime as _dt


class EfinanceClient:
    """
    最基本的 efinance 客户端封装，直接返回 efinance 的原始基础信息接口输出。
    """

    def __init__(self) -> None:
        try:
            import efinance as _ef  # type: ignore

            self._ef = _ef
            self._import_error: Optional[Exception] = None
        except Exception as e:  # pragma: no cover - import-time guard
            self._ef = None
            self._import_error = e

    def _ensure_efinance(self) -> None:
        if self._ef is None:
            msg = (
                "efinance 未安装或导入失败。请通过 `pip install efinance` 安装，"
                "或检查 efinance 导入错误："
                f"{self._import_error!r}"
            )
            raise RuntimeError(msg)

    def _resolve_getter(self):
        """
        Attempt to resolve efinance stock base info getter.
        Common usage: efinance.stock.get_base_info(stock_codes)
        Try multiple attribute access patterns for compatibility.
        """
        stock_mod = getattr(self._ef, "stock", None)
        if stock_mod is not None:
            func = getattr(stock_mod, "get_base_info", None)
            if callable(func):
                return func
            func = getattr(stock_mod, "get_realtime_summary", None)
            if callable(func):
                return func
        # fallback top-level function names
        func = getattr(self._ef, "get_base_info", None)
        if callable(func):
            return func
        return None

    def stock_individual_info_ef(self, stock_codes: Union[str, List[str]], **kwargs: Any) -> Any:
        """
        调用 efinance 获取 base info，直接返回 efinance 原始结果（不做任何映射或去除）。
        stock_codes: 单个代码字符串或代码列表，行为与 efinance.get_base_info 保持一致。
        """
        self._ensure_efinance()
        getter = self._resolve_getter()
        if not callable(getter):
            raise RuntimeError(
                "当前 efinance 版本不包含可用的股票基础信息获取接口（get_base_info/get_realtime_summary）"
            )
        raw = getter(stock_codes, **kwargs)
        return raw

    def stock_individual_basic_info_ef(self, stock_codes: Union[str, List[str]], **kwargs: Any) -> Any:
        """
        Alias for stock_individual_info_ef to match naming used for other clients.
        """
        return self.stock_individual_info_ef(stock_codes, **kwargs)
