import efinance as ef
from .base import BaseClient

API_MAPPING = {
    'stock_individual_info': ef.stock.get_base_info,
    # 可以继续添加更多 efinance API:
    # 'stock_realtime_data': ef.stock.get_realtime_quotes,
    # 'stock_history': ef.stock.get_quote_history,
    # 等等...
}

class EfinanceClient(BaseClient):


    def __init__(self):
        super().__init__()

    def fetch(self, api_name: str, params: dict = None):
        try:
            if api_name not in API_MAPPING:
                error_msg = f"Efinance does not have named '{api_name}' in API mapping"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            api_func = API_MAPPING[api_name]
            
            if params is None:
                params = {}
            
            self.logger.debug(f"Calling Efinance API: {api_name} with params: {params}")
            
            result = api_func(**params)
            
            self.logger.debug(f"Received data from Efinance API '{api_name}': {str(result)[:100]}...")
            
            self._save_raw_data(api_name, params, result)
            
            return result
                
        except Exception as e:
            error_msg = f"Error fetching data from Efinance API '{api_name}': {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
