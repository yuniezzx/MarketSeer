"""
股票相关工具函数
"""


def get_market_from_code(code):
    """
    根据股票代码判断所属市场

    中国A股市场规则：
    - 上海证券交易所(SH)：
      - 600xxx, 601xxx, 603xxx, 605xxx: 主板
      - 688xxx: 科创板
    - 深圳证券交易所(SZ)：
      - 000xxx, 001xxx: 主板
      - 002xxx: 中小板
      - 300xxx: 创业板
    - 北京证券交易所(BJ)：
      - 4xxxxx, 8xxxxx: 北交所

    Args:
        code (str): 股票代码

    Returns:
        str: 市场代码 ('SH', 'SZ', 'BJ', 'UNKNOWN')

    Examples:
        >>> get_market_from_code('600000')
        'SH'
        >>> get_market_from_code('000001')
        'SZ'
        >>> get_market_from_code('688001')
        'SH'
        >>> get_market_from_code('300001')
        'SZ'
    """
    if not code:
        return 'UNKNOWN'

    code_str = str(code).strip()

    # 上海证券交易所
    if code_str.startswith(('600', '601', '603', '605', '688')):
        return 'SH'

    # 深圳证券交易所
    if code_str.startswith(('000', '001', '002', '003', '300')):
        return 'SZ'

    # 北京证券交易所
    if code_str.startswith(('4', '8')) and len(code_str) == 6:
        return 'BJ'

    return 'UNKNOWN'


def format_stock_code(code, with_market=False):
    """
    格式化股票代码

    Args:
        code (str): 股票代码
        with_market (bool): 是否附加市场前缀

    Returns:
        str: 格式化后的股票代码

    Examples:
        >>> format_stock_code('600000')
        '600000'
        >>> format_stock_code('600000', with_market=True)
        'SH600000'
    """
    if not code:
        return ''

    code_str = str(code).strip()

    if with_market:
        market = get_market_from_code(code_str)
        return f"{market}{code_str}"

    return code_str
