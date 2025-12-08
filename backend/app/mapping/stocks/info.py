from typing import Dict, Any
from ..base_mapper import BaseMapper
from app.data_sources import ClientManager


class StockInfoMapper(BaseMapper):
    """
    StockInfo模型的映射器

    专门用于映射股票基础信息
    """

    def __init__(self, client_manager: ClientManager):
        """
        初始化StockInfo映射器

        Args:
            client_manager: 数据源客户端管理器
        """
        # 导入配置
        from ..stock_info_mapping import STOCK_INFO_FIELD_MAPPING, API_CONFIGS

        super().__init__(client_manager, STOCK_INFO_FIELD_MAPPING, API_CONFIGS)

    def map_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        映射股票基础信息

        Args:
            symbol: 股票代码

        Returns:
            映射后的股票信息字典
        """
        self.logger.info(f"Mapping stock info for symbol: {symbol}")
        return self.map_all_fields({'symbol': symbol})
