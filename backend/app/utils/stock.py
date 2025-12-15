def add_market_prefix(code: str) -> str:
    """
    为股票代码添加市场前缀 (用于雪球API)

    Args:
        code: 股票代码,如 "002156"

    Returns:
        带市场前缀的代码,如 "SZ002156"

    规则:
        - 0, 3 开头 -> 深圳 (SZ)
        - 6 开头 -> 上海 (SH)
        - 8, 4 开头 -> 北京 (BJ)
    """
    if code.startswith(('0', '3')):
        return f"SZ{code}"
    elif code.startswith('6'):
        return f"SH{code}"
    elif code.startswith('8') or code.startswith('4'):
        return f"BJ{code}"
    return code


def get_market_code(code: str) -> str:
    """获取市场代码（不含股票代码）"""
    if code.startswith(('0', '3')):
        return 'SZ'
    elif code.startswith('6'):
        return 'SH'
    elif code.startswith(('8', '4')):
        return 'BJ'
    return 'SZ'
