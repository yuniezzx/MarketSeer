import akshare as ak
from .base import BaseClient


class AkshareClient(BaseClient):
    def __init__(self):
        super().__init__()

    def fetch(self, api_name: str, params: dict = None):
        try:
            if not hasattr(ak, api_name):
                error_msg = f"Akshare does not have API named '{api_name}'"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            self.logger.debug(f"Calling Akshare API: {api_name} with params: {params}")

            api_func = getattr(ak, api_name)
            if params is None:
                params = {}

            result = api_func(**params)

            self.logger.debug(f"Received data from Akshare API '{api_name}': {str(result)[:100]}...")
            return result

        except Exception as e:
            error_msg = f"Error fetching data from Akshare API '{api_name}': {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
