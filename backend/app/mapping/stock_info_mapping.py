"""
股票基础信息字段映射配置

定义 StockInfo 模型各字段的数据源降级链和 API 配置
"""

# 字段映射配置
# key: StockInfo 模型字段名
# value: 降级链列表,按优先级从高到低排列
STOCK_INFO_FIELD_MAPPING = {
    # 基本信息
    'code': [
        {'api': 'stock_individual_info_em', 'field': '股票代码'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'stock_code'},
        {'api': 'stock_individual_info', 'field': '股票代码'}
    ],
    'name': [
        {'api': 'stock_individual_info_em', 'field': '股票简称'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'stock_name'},
        {'api': 'stock_individual_info', 'field': '股票简称'}
    ],
    'full_name': [
        {'api': 'stock_individual_info_em', 'field': '股票名称'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'name'},
        {'api': 'stock_individual_info', 'field': '股票名称'}
    ],
    
    # 市场信息
    'market': [
        {'api': 'stock_individual_info_em', 'field': '市场类型'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'exchange'},
        {'api': 'stock_individual_info', 'field': '市场'}
    ],
    
    # 行业分类
    'industry_code': [
        {'api': 'stock_individual_info_em', 'field': '行业代码'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'industry_code'}
    ],
    'industry': [
        {'api': 'stock_individual_info_em', 'field': '行业'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'industry_name'},
        {'api': 'stock_individual_info', 'field': '行业'}
    ],
    
    # 重要日期
    'establish_date': [
        {'api': 'stock_individual_info_em', 'field': '成立日期'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'establish_date'}
    ],
    'list_date': [
        {'api': 'stock_individual_info_em', 'field': '上市日期'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'list_date'},
        {'api': 'stock_individual_info', 'field': '上市日期'}
    ],
    
    # 主营范围
    'main_operation_business': [
        {'api': 'stock_individual_info_em', 'field': '主营业务'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'main_operation_business'}
    ],
    'operating_scope': [
        {'api': 'stock_individual_info_em', 'field': '经营范围'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'operating_scope'}
    ],
    
    # 状态信息
    'status': [
        {'api': 'stock_individual_info_em', 'field': '上市状态'},
        {'api': 'stock_individual_basic_info_xq', 'field': 'status'},
        {'api': 'stock_individual_info', 'field': '上市状态'}
    ]
}

# API 配置
# key: API 名称
# value: 数据源和参数映射配置
API_CONFIGS = {
    # akshare 数据源的 API 配置
    'stock_individual_info_em': {
        'data_source': 'akshare',
        'param_mapping': {
            'symbol': 'symbol'  # StockInfoMapper传入的参数名 -> API实际参数名
        }
    },
    'stock_individual_basic_info_xq': {
        'data_source': 'akshare',
        'param_mapping': {
            'symbol': 'symbol'
        }
    },
    
    # efinance 数据源的 API 配置
    'stock_individual_info': {
        'data_source': 'efinance',
        'param_mapping': {
            'symbol': 'stock_code'  # efinance 使用 stock_code 参数
        }
    }
}

# 配置说明
"""
字段映射配置说明:

1. 降级链优先级:
   - 列表中的顺序表示优先级,从高到低
   - 当第一个数据源失败时,自动尝试下一个
   - 所有数据源都失败时,该字段返回 None

2. API 配置说明:
   - data_source: 数据源名称,对应 ClientManager 中的客户端
   - param_mapping: 参数映射,将通用参数名映射到特定 API 的参数名
   
3. 字段路径:
   - 支持简单字段名: '股票代码'
   - 支持点号分隔的嵌套路径: 'data.stock_code'
   - 自动处理 DataFrame 和 dict 两种数据格式

4. 扩展方式:
   - 添加新字段: 在 STOCK_INFO_FIELD_MAPPING 中添加字段及其降级链
   - 添加新数据源: 在 API_CONFIGS 中添加新 API 配置
   - 添加新 API: 实现对应的数据源客户端方法

示例使用:
    from app.mapping import StockInfoMapper
    from app.data_sources.client_manager import ClientManager
    
    client_manager = ClientManager()
    mapper = StockInfoMapper(client_manager)
    
    # 映射所有字段
    all_fields = mapper.map_all_fields({'symbol': '600000'})
"""
