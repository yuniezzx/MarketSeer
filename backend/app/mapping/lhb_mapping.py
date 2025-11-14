"""
龙虎榜（LHB）数据映射配置
定义从 akshare 接口到 WeeklyLHB 模型的字段映射关系
"""

# akshare 接口返回的字段映射
LHB_FIELD_MAPPING = {
    "code": "代码",
    "name": "名称",
    "listed_date": "上榜日",
    "analysis": "解读",
    "close_price": "收盘价",
    "change_percent": "涨跌幅",
    "turnover_rate": "换手率",
    "circulating_market_cap": "流通市值",
    "reasons": "上榜原因",
    "return_1d": "上榜后1日",
    "return_5d": "上榜后5日",
    "return_10d": "上榜后10日",
}

def weekly_lhb_mapper(raw_source):
    """
    将 akshare 龙虎榜原始数据映射为 WeeklyLHB 所需格式

    Args:
        raw_source: dict 或 list，akshare 返回的单条或多条龙虎榜数据

    Returns:
        dict 或 list: 映射后的数据（dict 或 dict 列表）
    """
    def try_float(val):
        try:
            return float(val)
        except Exception:
            return None

    def map_one(item):
        mapped = {}
        for model_field, source_field in LHB_FIELD_MAPPING.items():
            value = item.get(source_field)
            # 类型转换
            if model_field in ["close_price", "change_percent", "turnover_rate", "circulating_market_cap", "return_1d", "return_5d", "return_10d"]:
                mapped[model_field] = try_float(value)
            else:
                mapped[model_field] = value
        return mapped

    if isinstance(raw_source, list):
        return [map_one(item) for item in raw_source]
    elif isinstance(raw_source, dict):
        return map_one(raw_source)
    else:
        return None
