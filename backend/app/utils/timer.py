from datetime import datetime, date
from typing import Optional, Union
import exchange_calendars as xcals
from functools import lru_cache
import pandas as pd


@lru_cache(maxsize=1)
def _get_china_calendar():
    """
    获取中国股市交易日历（上海证券交易所）
    使用缓存避免重复加载

    Returns:
        ExchangeCalendar: 上海证券交易所交易日历
    """
    return xcals.get_calendar("XSHG")


def convert_to_date(value: Optional[Union[int, float, str, date]]) -> Optional[date]:
    """
    将各种格式的日期数据转换为 Python date 对象

    支持的输入格式:
    - 毫秒时间戳 (如 760291200000)
    - 秒时间戳 (如 760291200)
    - 字符串日期 (如 "20070816" 或 "2007-08-16")
    - date 对象 (直接返回)
    - None/空字符串 (返回 None)

    Args:
        value: 日期数据，可以是多种格式

    Returns:
        Python date 对象，失败返回 None
    """
    if value is None or value == "":
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, (int, float)):
        try:
            if value > 10000000000:  # 毫秒时间戳
                return datetime.fromtimestamp(value / 1000).date()
            else:  # 秒时间戳
                return datetime.fromtimestamp(value).date()
        except (ValueError, OSError):
            return None

    # 字符串日期
    if isinstance(value, str):
        try:
            # 尝试格式 "20070816"
            if len(value) == 8 and value.isdigit():
                return datetime.strptime(value, "%Y%m%d").date()
            # 尝试格式 "2007-08-16"
            elif "-" in value:
                return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    return None


def is_trading_day(check_date: Optional[Union[str, date, datetime]] = None) -> bool:
    """
    判断指定日期是否为中国股市交易日

    使用上海证券交易所(XSHG)的交易日历进行判断。
    交易日是指股市开放交易的工作日，排除周末、节假日等非交易日。

    Args:
        check_date: 要检查的日期，支持以下格式:
            - None: 检查今天
            - date 对象: 直接使用
            - datetime 对象: 自动提取日期部分
            - 字符串: "20240101" 或 "2024-01-01" 格式

    Returns:
        bool: True 表示是交易日，False 表示非交易日

    Examples:
        >>> is_trading_day()  # 检查今天
        True
        >>> is_trading_day("2024-01-01")  # 检查元旦
        False
        >>> is_trading_day(date(2024, 1, 2))  # 检查指定日期
        True
    """
    # 获取交易日历
    calendar = _get_china_calendar()

    # 处理输入日期
    if check_date is None:
        check_date = date.today()
    elif isinstance(check_date, datetime):
        check_date = check_date.date()
    elif isinstance(check_date, str):
        check_date = convert_to_date(check_date)
        if check_date is None:
            raise ValueError(f"无效的日期格式")
    elif not isinstance(check_date, date):
        raise TypeError(f"不支持的日期类型: {type(check_date)}")

    # 使用 exchange-calendars 判断是否为交易日
    check_timestamp = pd.Timestamp(check_date)
    return calendar.is_session(check_timestamp)
