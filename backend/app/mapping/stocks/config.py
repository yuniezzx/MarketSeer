"""
股票基础信息映射配置 - API级降级机制

定义 StockInfo 模型的 API 优先级链、参数转换器和字段映射
"""

from typing import Callable
from app.utils import add_market_prefix

# ============ 参数转换函数 ============


def no_transform(code: str) -> str:
    """
    不转换,直接返回原值

    Args:
        code: 股票代码

    Returns:
        原始股票代码
    """
    return code


# ============ API 优先级链 ============

API_PRIORITY_CHAIN = [
    'stock_individual_info_em',  # 优先级1: 东方财富 (字段最全)
    'stock_individual_basic_info_xq',  # 优先级2: 雪球 (补充缺失字段)
    'stock_individual_info',  # 优先级3: efinance (兜底)
]


# ============ API 配置(含参数转换器) ============

API_CONFIGS = {
    'stock_individual_info_em': {
        'data_source': 'akshare',
        'param_mapping': {'symbol': 'symbol'},  # StockInfoMapper传入参数 -> API实际参数
        'param_transformer': no_transform,  # 参数格式: 002156
    },
    'stock_individual_basic_info_xq': {
        'data_source': 'akshare',
        'param_mapping': {'symbol': 'symbol'},
        'param_transformer': add_market_prefix,  # 参数格式: SZ002156
    },
    'stock_individual_info': {
        'data_source': 'efinance',
        'param_mapping': {'symbol': 'stock_code'},  # efinance 使用 stock_code 参数名
        'param_transformer': no_transform,  # 参数格式: 002156
    },
}


# ============ API 字段映射 ============

API_FIELD_MAPPING = {
    # 东方财富 API 字段映射
    'stock_individual_info_em': {
        'code': '股票代码',
        'name': '股票简称',
        'full_name': '股票名称',
        'market': '市场类型',
        'industry_code': '行业代码',
        'industry': '行业',
        'establish_date': '成立日期',
        'list_date': '上市日期',
        'main_operation_business': '主营业务',
        'operating_scope': '经营范围',
        'status': '上市状态',
    },
    # 雪球 API 字段映射
    'stock_individual_basic_info_xq': {
        'code': 'stock_code',
        'name': 'stock_name',
        'full_name': 'name',
        'market': 'exchange',
        'industry_code': 'industry_code',
        'industry': 'industry_name',
        'establish_date': 'establish_date',
        'list_date': 'list_date',
        'main_operation_business': 'main_operation_business',
        'operating_scope': 'operating_scope',
        'status': 'status',
    },
    # efinance API 字段映射
    'stock_individual_info': {
        'code': '股票代码',
        'name': '股票简称',
        'full_name': '股票名称',
        'market': '市场',
        'industry': '行业',
        'list_date': '上市日期',
        'status': '上市状态',
    },
}


# ============ 所有支持的字段列表 ============

ALL_FIELDS = [
    'code',  # 股票代码
    'name',  # 股票简称
    'full_name',  # 股票全称
    'market',  # 市场类型
    'industry_code',  # 行业代码
    'industry',  # 行业名称
    'establish_date',  # 成立日期
    'list_date',  # 上市日期
    'main_operation_business',  # 主营业务
    'operating_scope',  # 经营范围
    'status',  # 上市状态
]


# ============ 配置说明 ============

"""
API 级降级机制说明:

1. 工作流程:
   - 按 API_PRIORITY_CHAIN 顺序尝试每个 API
   - 每个 API 最多只调用一次
   - 提取所有可映射的字段
   - 检查是否还有字段缺失
   - 有缺失且还有下一个 API 时继续尝试
   - 增量合并结果,不覆盖已获取的字段

2. 参数转换:
   - 每个 API 可配置独立的参数转换器
   - 在调用 API 前自动转换参数格式
   - 支持自定义转换函数

3. 字段映射:
   - API_FIELD_MAPPING 定义每个 API 返回数据到模型字段的映射
   - 支持简单字段名和嵌套路径 (如 'data.stock_code')
   - 自动处理 DataFrame 和 dict 两种数据格式

4. 扩展方式:
   - 添加新 API: 在三个配置中添加对应项
   - 添加新字段: 在 API_FIELD_MAPPING 和 ALL_FIELDS 中添加
   - 调整优先级: 修改 API_PRIORITY_CHAIN 的顺序

示例使用:
    from app.mapping.stocks import StockInfoMapper
    from app.data_sources.client_manager import ClientManager
    
    client_manager = ClientManager()
    mapper = StockInfoMapper(client_manager)
    
    # 映射所有字段,自动降级
    result = mapper.map_all_fields({'symbol': '002156'})
    # result = {'code': '002156', 'name': '通富微电', ...}
"""
