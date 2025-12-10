from logger import logger
from .akshare_client import AkshareClient
from .efinance_client import EfinanceClient


class ClientManager:
    data_sources = {
        "akshare": AkshareClient,
        "efinance": EfinanceClient,
    }

    def __init__(self):
        """初始化客户端管理器"""
        self._clients = {}

    def get_client(self, data_source: str):
        """
        获取指定数据源的客户端实例
        
        Args:
            data_source: 数据源名称 (如 'akshare', 'efinance')
            
        Returns:
            对应的客户端实例
        """
        if data_source not in self.data_sources:
            raise ValueError(f"Unknown data source: {data_source}")
        
        # 使用缓存的客户端实例
        if data_source not in self._clients:
            self._clients[data_source] = self.data_sources[data_source]()
        
        return self._clients[data_source]
