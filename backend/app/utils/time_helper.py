"""
时间处理工具
"""

from datetime import datetime, timedelta, date
from typing import Optional, Union
import exchange_calendars as xcals
from logger import logger


def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    """
    格式化日期时间

    Args:
        dt: datetime 对象
        fmt: 格式字符串

    Returns:
        str: 格式化后的时间字符串
    """
    if isinstance(dt, datetime):
        return dt.strftime(fmt)
    return str(dt)


def parse_datetime(date_str, fmt='%Y-%m-%d %H:%M:%S'):
    """
    解析日期时间字符串

    Args:
        date_str: 日期时间字符串
        fmt: 格式字符串

    Returns:
        datetime: datetime 对象
    """
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        # 尝试 ISO 格式
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            return None


def get_current_time(fmt='%Y-%m-%d %H:%M:%S'):
    """
    获取当前时间

    Args:
        fmt: 格式字符串，如果为 None 则返回 datetime 对象

    Returns:
        str or datetime: 当前时间
    """
    now = datetime.now()
    if fmt:
        return now.strftime(fmt)
    return now


def get_date_range(days=7):
    """
    获取日期范围

    Args:
        days: 天数

    Returns:
        tuple: (开始日期, 结束日期)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


class TradingCalendar:
    """交易日历类"""

    # 支持的交易所日历
    CALENDARS = {
        'CN': 'XSHG',  # 中国上海证券交易所
        'SHSE': 'XSHG',  # 上海证券交易所
        'SZSE': 'XSHE',  # 深圳证券交易所
        'US': 'XNYS',  # 美国纽约证券交易所
        'NYSE': 'XNYS',  # 纽约证券交易所
        'NASDAQ': 'XNAS',  # 纳斯达克
        'HK': 'XHKG',  # 香港交易所
    }

    def __init__(self, market: str = 'CN'):
        """
        初始化交易日历

        Args:
            market: 市场代码，支持 'CN', 'US', 'HK' 等
        """
        self.market = market.upper()
        calendar_code = self.CALENDARS.get(self.market, 'XSHG')
        try:
            self.calendar = xcals.get_calendar(calendar_code)
            logger.info(f"成功加载 {market} 市场日历 ({calendar_code})")
        except Exception as e:
            logger.error(f"加载市场日历失败: {e}")
            # 默认使用上海证券交易所日历
            self.calendar = xcals.get_calendar('XSHG')

    def is_trading_day(self, check_date: Optional[Union[date, datetime, str]] = None) -> bool:
        """
        判断指定日期是否为交易日

        Args:
            check_date: 要检查的日期，可以是 date、datetime 对象或字符串格式 'YYYY-MM-DD'
                       如果为 None，则检查今天

        Returns:
            bool: True 表示是交易日，False 表示不是交易日
        """
        try:
            # 处理日期参数
            if check_date is None:
                check_date = datetime.now().date()
            elif isinstance(check_date, str):
                check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
            elif isinstance(check_date, datetime):
                check_date = check_date.date()

            # 使用 exchange-calendars 判断是否为交易日
            is_trading = self.calendar.is_session(check_date)

            logger.debug(f"{check_date} 是否为交易日: {is_trading}")
            return is_trading

        except Exception as e:
            logger.error(f"判断交易日时出错: {e}")
            return False

    def is_today_trading_day(self) -> bool:
        """
        判断今天是否为交易日

        Returns:
            bool: True 表示今天是交易日，False 表示不是交易日
        """
        return self.is_trading_day()

    def get_previous_trading_day(self, check_date: Optional[Union[date, datetime, str]] = None) -> date:
        """
        获取指定日期之前的最近一个交易日

        Args:
            check_date: 参考日期，如果为 None 则使用今天

        Returns:
            date: 上一个交易日
        """
        try:
            if check_date is None:
                check_date = datetime.now().date()
            elif isinstance(check_date, str):
                check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
            elif isinstance(check_date, datetime):
                check_date = check_date.date()

            prev_day = self.calendar.previous_session(check_date)
            return prev_day.date() if hasattr(prev_day, 'date') else prev_day

        except Exception as e:
            logger.error(f"获取上一个交易日时出错: {e}")
            return check_date

    def get_next_trading_day(self, check_date: Optional[Union[date, datetime, str]] = None) -> date:
        """
        获取指定日期之后的最近一个交易日

        Args:
            check_date: 参考日期，如果为 None 则使用今天

        Returns:
            date: 下一个交易日
        """
        try:
            if check_date is None:
                check_date = datetime.now().date()
            elif isinstance(check_date, str):
                check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
            elif isinstance(check_date, datetime):
                check_date = check_date.date()

            next_day = self.calendar.next_session(check_date)
            return next_day.date() if hasattr(next_day, 'date') else next_day

        except Exception as e:
            logger.error(f"获取下一个交易日时出错: {e}")
            return check_date

    def get_trading_days_in_range(
        self, start_date: Union[date, datetime, str], end_date: Union[date, datetime, str]
    ) -> list:
        """
        获取日期范围内的所有交易日

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            list: 交易日列表
        """
        try:
            # 处理日期参数
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            elif isinstance(start_date, datetime):
                start_date = start_date.date()

            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            elif isinstance(end_date, datetime):
                end_date = end_date.date()

            # 获取交易日
            sessions = self.calendar.sessions_in_range(start_date, end_date)
            trading_days = [s.date() if hasattr(s, 'date') else s for s in sessions]

            return trading_days

        except Exception as e:
            logger.error(f"获取交易日范围时出错: {e}")
            return []


# 创建默认实例（中国市场）
_default_calendar = None


def get_trading_calendar(market: str = 'CN') -> TradingCalendar:
    """
    获取交易日历实例

    Args:
        market: 市场代码

    Returns:
        TradingCalendar: 交易日历实例
    """
    return TradingCalendar(market)


def is_trading_day(check_date: Optional[Union[date, datetime, str]] = None, market: str = 'CN') -> bool:
    """
    判断指定日期是否为交易日（便捷函数）

    Args:
        check_date: 要检查的日期，如果为 None 则检查今天
        market: 市场代码，默认为中国市场

    Returns:
        bool: True 表示是交易日，False 表示不是交易日

    Examples:
        >>> is_trading_day()  # 检查今天是否为交易日
        >>> is_trading_day('2024-01-01')  # 检查指定日期
        >>> is_trading_day(datetime.now(), market='US')  # 检查美国市场
    """
    global _default_calendar
    if _default_calendar is None or _default_calendar.market != market.upper():
        _default_calendar = TradingCalendar(market)
    return _default_calendar.is_trading_day(check_date)


def is_today_trading_day(market: str = 'CN') -> bool:
    """
    判断今天是否为交易日（便捷函数）

    Args:
        market: 市场代码，默认为中国市场

    Returns:
        bool: True 表示今天是交易日，False 表示不是交易日

    Examples:
        >>> is_today_trading_day()  # 检查中国市场今天是否为交易日
        >>> is_today_trading_day('US')  # 检查美国市场
    """
    return is_trading_day(None, market)
