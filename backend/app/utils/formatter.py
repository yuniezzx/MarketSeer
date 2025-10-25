"""
数据格式化工具
"""


def format_number(num, decimals=2):
    """
    格式化数字
    
    Args:
        num: 数字
        decimals: 小数位数
    
    Returns:
        str: 格式化后的数字字符串
    """
    try:
        if num is None:
            return 'N/A'
        return f"{float(num):.{decimals}f}"
    except (ValueError, TypeError):
        return str(num)


def format_percentage(value, decimals=2):
    """
    格式化百分比
    
    Args:
        value: 数值（0-1 或 0-100）
        decimals: 小数位数
    
    Returns:
        str: 格式化后的百分比字符串
    """
    try:
        if value is None:
            return 'N/A'
        
        num = float(value)
        
        # 如果值在 0-1 之间，认为是小数形式，需要乘以 100
        if 0 <= num <= 1:
            num *= 100
        
        return f"{num:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_large_number(num):
    """
    格式化大数字（添加千分位分隔符）
    
    Args:
        num: 数字
    
    Returns:
        str: 格式化后的数字字符串
    """
    try:
        if num is None:
            return 'N/A'
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return str(num)


def format_currency(amount, currency='¥', decimals=2):
    """
    格式化货币
    
    Args:
        amount: 金额
        currency: 货币符号
        decimals: 小数位数
    
    Returns:
        str: 格式化后的货币字符串
    """
    try:
        if amount is None:
            return 'N/A'
        return f"{currency}{float(amount):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(amount)
