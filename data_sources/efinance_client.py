from __future__ import annotations
from typing import Union, Any, Callable, Literal, List
import pandas as pd
import efinance as ef
from utils.logger import get_data_sources_logger
from data_sources.helpers import (
    DateLike, normalize_stock_code, detect_market_prefix,
    to_em_date, safe_call
)


# ============ Logging ============
logger = get_data_sources_logger("datasource.efinance")


# ============ Stock ============
""" efinance-个股基础信息 """
@safe_call(cache=True)
def get_profile_ef(stock_code: Union[str, List[str]]) -> pd.DataFrame:
    if isinstance(stock_code, str):
        codes = [normalize_stock_code(stock_code)]
    elif isinstance(stock_code, list):
        codes = [normalize_stock_code(c) for c in stock_code]
    else:
        raise TypeError(f"stock_code must be str or List[str], got {type(stock_code)}")

    result = ef.stock.get_base_info(codes if len(codes) > 1 else codes[0])

    if isinstance(result, pd.Series):
        return result.to_frame().T
    return result


__all__ = [
    "get_profile_ef"
    ]