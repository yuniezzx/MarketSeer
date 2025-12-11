from typing import Dict, Any
from ..base_mapper import BaseMapper
from app.data_sources import ClientManager
from .config import (
    API_PRIORITY_CHAIN,
    API_CONFIGS,
    API_FIELD_MAPPING,
    ALL_FIELDS
)


class StockInfoMapper(BaseMapper):
    """
    StockInfo模型的映射器

    专门用于映射股票基础信息,使用API级降级机制
    """

    def __init__(self, client_manager: ClientManager):
        """
        初始化 StockInfoMapper
        
        Args:
            client_manager: 数据源客户端管理器
        """
        super().__init__(
            client_manager=client_manager,
            api_priority_chain=API_PRIORITY_CHAIN,
            api_configs=API_CONFIGS,
            api_field_mapping=API_FIELD_MAPPING,
            all_fields=ALL_FIELDS
        )
