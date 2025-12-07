from logger import logger
from .akshare_client import AkshareClient
from .efinance_client import EfinanceClient


class ClientManager:
    data_sources = {
        "akshare": AkshareClient,
        "efinance": EfinanceClient,
    }

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
