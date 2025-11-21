"""
龙虎榜数据映射配置
定义从akshare数据源到 WeeklyLHB 模型的字段映射关系
"""

# akshare龙虎榜数据源映射
# stock_lhb_detail_em 接口返回的字段映射
LHB_FIELD_MAPPING = {
    'code': '代码',  # WeeklyLHB.code <- lhb_data['代码']
    'name': '名称',  # WeeklyLHB.name <- lhb_data['名称']
    'listed_date': '上榜日',  # WeeklyLHB.listed_date <- lhb_data['上榜日']
    'close_price': '收盘价',  # WeeklyLHB.close_price <- lhb_data['收盘价']
    'change_percent': '涨跌幅',  # WeeklyLHB.change_percent <- lhb_data['涨跌幅']
    'turnover_rate': '换手率',  # WeeklyLHB.turnover_rate <- lhb_data['换手率']
    'circulating_market_cap': '流通市值',  # WeeklyLHB.circulating_market_cap <- lhb_data['流通市值']
    'lhb_buy_amount': '龙虎榜买入额',  # WeeklyLHB.lhb_buy_amount <- lhb_data['龙虎榜买入额']
    'lhb_sell_amount': '龙虎榜卖出额',  # WeeklyLHB.lhb_sell_amount <- lhb_data['龙虎榜卖出额']
    'lhb_net_amount': '龙虎榜净买额',  # WeeklyLHB.lhb_net_amount <- lhb_data['龙虎榜净买额']
    'lhb_trade_amount': '龙虎榜成交额',  # WeeklyLHB.lhb_trade_amount <- lhb_data['龙虎榜成交额']
    'market_total_amount': '市场总成交额',  # WeeklyLHB.market_total_amount <- lhb_data['市场总成交额']
    'lhb_net_ratio': '净买额占总成交比',  # WeeklyLHB.lhb_net_ratio <- lhb_data['净买额占总成交比']
    'lhb_trade_ratio': '成交额占总成交比',  # WeeklyLHB.lhb_trade_ratio <- lhb_data['成交额占总成交比']
    'analysis': '解读',  # WeeklyLHB.analysis <- lhb_data['解读']
    'reasons': '上榜原因',  # WeeklyLHB.reasons <- lhb_data['上榜原因']
    # 如需添加新字段,在这里添加:
    # 'new_field': 'source_field_name',  # 注释说明映射关系
}

def weekly_lhb_mapper(item: dict) -> dict:
    """
    将akshare的龙虎榜数据映射为 WeeklyLHB 所需格式

    Args:
        item: 来自akshare的数据字典

    Returns:
        dict: 映射后的龙虎榜信息字典
    """
    mapped_data = {}

    # 映射akshare龙虎榜数据
    for model_field, source_field in LHB_FIELD_MAPPING.items():
        if source_field in item:
            value = item[source_field]
            
            # 根据字段类型进行数据转换
            if model_field in ['code', 'name', 'analysis', 'reasons']:
                # 字符串类型字段
                mapped_data[model_field] = str(value) if value is not None else ''
            elif model_field == 'listed_date':
                # 日期类型字段,保持原样
                mapped_data[model_field] = value
            else:
                # 数值类型字段(Float)
                mapped_data[model_field] = float(value) if value is not None else 0.0

    return mapped_data
