# Akshare client wrapper with stock_info mapping
# Provides:
# - stock_individual_info_em -> mapped dict matching models.stock.StockInfo where possible
# - stock_individual_basic_info_xq -> mapped dict matching models.stock.StockInfo where possible

from typing import Any, Optional, Dict


class AkshareClient:
    """
    最基本的 Akshare 客户端封装，包含对 stock info 的映射到 StockInfo 字段。
    """

    def __init__(self) -> None:
        try:
            import akshare as _ak  # type: ignore

            self._ak = _ak
            self._import_error: Optional[Exception] = None
        except Exception as e:  # pragma: no cover - import-time guard
            self._ak = None
            self._import_error = e

    def _ensure_ak(self) -> None:
        if self._ak is None:
            msg = (
                "akshare 未安装或导入失败。请通过 `pip install akshare` 安装，"
                "或检查 akshare 导入错误："
                f"{self._import_error!r}"
            )
            raise RuntimeError(msg)

    def stock_individual_info_em(self, symbol: str, **kwargs: Any) -> Any:
        """
        获取东方财富/EM 相关的个股信息并映射为 StockInfo 相关字段的字典。
        若无法映射，将返回 akshare 的原始结果以保持向后兼容。
        """
        self._ensure_ak()
        func = getattr(self._ak, "stock_individual_info_em", None)
        if not callable(func):
            raise RuntimeError("当前 akshare 版本不包含 'stock_individual_info_em' 接口。")
        raw = func(symbol, **kwargs)
        try:
            mapped = self._map_to_stock_info(raw, symbol=symbol)
            if mapped and ("symbol" in mapped or "code" in mapped or "name" in mapped):
                return mapped
            return raw
        except Exception:
            return raw

    def stock_individual_basic_info_xq(self, symbol: str, **kwargs: Any) -> Any:
        """
        获取雪球的个股基础信息并映射为 StockInfo 相关字段的字典。
        akshare 的此接口接受类似 "SH601127" / "SZ000001" 的带市场前缀格式。
        为兼容传入纯数字代码（例如 "002104" 或 "600519"）或带后缀的形式（"002104.SZ"），
        在调用前尝试统一为带前缀的形式（"SH"/"SZ" + code）。
        行为与 stock_individual_info_em 类似。
        """
        self._ensure_ak()
        func = getattr(self._ak, "stock_individual_basic_info_xq", None)
        if not callable(func):
            # 部分 akshare 版本可能使用不同名称，尝试兼容函数名
            func = getattr(self._ak, "stock_individual_info_xq", None)
        if not callable(func):
            raise RuntimeError(
                "当前 akshare 版本不包含 'stock_individual_basic_info_xq' / 'stock_individual_info_xq' 接口。"
            )

        # Prepare symbol in the format expected by akshare: prefer "SHxxxxxx" or "SZxxxxxx"
        symbol_for_call = str(symbol).strip()
        try:
            # If symbol provided like "002104.SZ" or "600519.SH", convert to "SZ002104" / "SH600519"
            if "." in symbol_for_call:
                parts = symbol_for_call.split(".")
                code_part = parts[0]
                suffix = parts[1].upper() if len(parts) > 1 else ""
                if suffix in ("SH", "SZ") and code_part.isdigit():
                    symbol_for_call = f"{suffix}{code_part}"
            else:
                up = symbol_for_call.upper()
                # already in "SH600519" / "SZ000001" format
                if up.startswith(("SH", "SZ")) and up[2:].isdigit():
                    symbol_for_call = up
                else:
                    # pure numeric code -> infer market by prefix rule
                    code_only = symbol_for_call
                    if code_only.isdigit():
                        if code_only.startswith(("6", "9")):
                            symbol_for_call = f"SH{code_only}"
                        else:
                            symbol_for_call = f"SZ{code_only}"
                    else:
                        # fallback: leave as-is
                        symbol_for_call = symbol_for_call
        except Exception:
            # on any error, fall back to original input
            symbol_for_call = str(symbol).strip()

        raw = func(symbol_for_call, **kwargs)
        try:
            # pass original symbol as context to mapping
            mapped = self._map_to_stock_info(raw, symbol=symbol)
            if mapped and ("symbol" in mapped or "code" in mapped or "name" in mapped):
                return mapped
            return raw
        except Exception:
            return raw
