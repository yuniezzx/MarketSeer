from datetime import datetime, date
from typing import Optional, Union


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
    if value is None or value == '':
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
                return datetime.strptime(value, '%Y%m%d').date()
            # 尝试格式 "2007-08-16"
            elif '-' in value:
                return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None

    return None
