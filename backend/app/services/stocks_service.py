from typing import Optional
from .base_service import BaseService
from app.repository import StockInfoRepository
from app.mapping import map_stock_info
from app.data_sources import ClientManager


class StocksService(BaseService):
    def __init__(self):
        super().__init__()
        self.stock_repo = StockInfoRepository()

    def add_stock(self, symbol: str):
        """通过 symbol 从数据源获取并保存股票信息"""
        stock_data = map_stock_info(symbol, ClientManager())

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

    def list_stocks(
        self, offset: int = 0, limit: Optional[int] = None, order_by: Optional[str] = None, desc: bool = False
    ):
        """获取所有股票列表,支持分页和排序"""
        stocks = self.stock_repo.get_all(offset=offset, limit=limit, order_by=order_by, desc=desc)
        print(stocks)
        return [
            {
                'code': stock.code,
                'name': stock.name,
                'market': stock.market,
                'industry': stock.industry,
                'establish_date': stock.establish_date,
                'list_date': stock.list_date,
                'main_operation_business': stock.main_operation_business,
                'operating_scope': stock.operating_scope,
                'status': stock.status,
                'tracking': stock.tracking,
            }
            for stock in stocks
        ]
