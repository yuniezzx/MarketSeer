"""
股票数据映射配置
定义从不同数据源到 StockInfo 模型的字段映射关系
"""
from datetime import datetime

# 东方财富(EM)数据源映射
# stock_individual_info_em 接口返回的字段映射
EM_FIELD_MAPPING = {
    'code': '股票代码',  # StockInfo.code <- em_info_data['股票代码']
    'name': '股票简称',  # StockInfo.name <- em_info_data['股票简称']
}

# 雪球(XQ)数据源映射
# stock_individual_basic_info_xq 接口返回的字段映射
XQ_FIELD_MAPPING = {
    'full_name': 'org_name_cn',  # StockInfo.full_name <- xq_info_data['org_name_cn']
    'industry_code': 'affiliate_industry',  # StockInfo.industry_code <- xq_info_data['affiliate_industry']['ind_code']
    'industry': 'industry',  # StockInfo.industry <- xq_info_data['affiliate_industry']['ind_name']
    'establish_date': 'established_date',  # StockInfo.establish_date <- xq_info_data['established_date']
    'list_date': 'listed_date',  # StockInfo.list_date <- xq_info_data['listed_date']
    'main_operation_business': 'main_operation_business',  # StockInfo.main_operation_business <- xq_info_data['main_operation_business']
    'operating_scope': 'operating_scope',  # StockInfo.operating_scope <- xq_info_data['operating_scope']
    # 如需添加新字段，在这里添加：
    # 'new_field': 'source_field_name',  # 注释说明映射关系
}


def stock_info_mapper(em_source, xq_source):
    """
    将不同数据源的数据映射为 StockInfo 所需格式

    Args:
        em_source: 来自东方财富的数据字典
        xq_source: 来自雪球的数据字典

    Returns:
        dict: 映射后的股票信息字典
    """
    mapped_data = {}

    # 处理数据源为字典
    em_dict = {}
    if isinstance(em_source, list):
        em_dict = {item['item']: item['value'] for item in em_source if 'item' in item and 'value' in item}
    elif isinstance(em_source, dict):
        em_dict = em_source

    xq_dict = {}
    if isinstance(xq_source, list):
        xq_dict = {item['item']: item['value'] for item in xq_source if 'item' in item and 'value' in item}
    elif isinstance(xq_source, dict):
        xq_dict = xq_source

    # 映射东方财富数据
    if em_dict:
        for model_field, source_field in EM_FIELD_MAPPING.items():
            if source_field in em_dict:
                mapped_data[model_field] = em_dict[source_field]

    # 映射雪球数据
    if xq_dict:
        for model_field, source_field in XQ_FIELD_MAPPING.items():
            if model_field == 'industry_code':
                if 'affiliate_industry' in xq_dict and isinstance(xq_dict['affiliate_industry'], dict):
                    mapped_data[model_field] = xq_dict['affiliate_industry'].get('ind_code')
            elif model_field == 'industry':
                if 'affiliate_industry' in xq_dict and isinstance(xq_dict['affiliate_industry'], dict):
                    mapped_data[model_field] = xq_dict['affiliate_industry'].get('ind_name')
            elif model_field in ['establish_date', 'list_date']:
                # 处理日期字段:将时间戳转换为日期字符串
                if source_field in xq_dict and xq_dict[source_field]:
                    timestamp = xq_dict[source_field]
                    if isinstance(timestamp, (int, float)):
                        # 毫秒时间戳转换为日期字符串
                        dt = datetime.fromtimestamp(timestamp / 1000)
                        mapped_data[model_field] = dt.strftime('%Y-%m-%d')
                    elif isinstance(timestamp, str):
                        # 如果已经是字符串,直接使用
                        mapped_data[model_field] = timestamp
            else:
                if source_field in xq_dict:
                    mapped_data[model_field] = xq_dict[source_field]

    return mapped_data
