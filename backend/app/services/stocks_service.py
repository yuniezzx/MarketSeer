from .base_service import BaseService
from app.repository import StockInfoRepository
from app.mapping import StockInfoMapper
from app.data_sources import ClientManager


class StocksService(BaseService):
    def __init__(self):
        super().__init__()
        self.stock_repo = StockInfoRepository()
        self.stock_mapper = StockInfoMapper(ClientManager())

    def add_stock(self, symbol: str):
        """通过 symbol 从数据源获取并保存股票信息"""
        stock_data = self.stock_mapper.map_stock_info(symbol)

        if not stock_data:
            self.logger.info(f"获取到的股票数据: {stock_data}")
            raise ValueError(f"无法获取股票信息，symbol: {symbol}")

        stock = self.stock_repo.upsert_by_code(**stock_data)

        if stock:
            self.logger.info(f"股票信息已保存或更新: {stock.code} - {stock.name}")
            return {
                'code': stock.code,
                'name': stock.name,
                'market': stock.market,
                'industry': stock.industry,
                'status': stock.status,
            }
