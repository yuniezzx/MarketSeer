"""
时间处理工具
"""
from datetime import datetime, timedelta


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
