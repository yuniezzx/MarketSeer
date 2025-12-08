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

    @staticmethod
    def fetch(sapi_name: str, params: dict = None):
        """尝试从多个数据源获取数据"""
        errors = []

        for source_name, source_class in ClientManager.data_sources.items():
            try:
                logger.debug(f"Trying data source: {source_name}")
                client = source_class()
                result = client.fetch(sapi_name, params)
                logger.info(f"Successfully fetched from {source_name}")
                return result

            except Exception as e:
                error_msg = f"Data source '{source_name}' failed: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        # 如果全部失败
        full_error = f"All data sources failed for API '{sapi_name}'. Errors: " + "; ".join(errors)
        logger.critical(full_error)
        raise RuntimeError(full_error)
