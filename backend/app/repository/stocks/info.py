from app.models.stocks.info import StockInfo
from ..base import BaseRepository


class StockInfoRepository(BaseRepository[StockInfo]):
    """股票信息 Repository"""

    def __init__(self):
        super().__init__(StockInfo)

    def get_by_code(self, code: str) -> StockInfo:
        """根据股票代码获取股票信息"""
        return self.get_by_field('code', code)

    def get_by_market(self, market: str):
        """根据市场获取股票列表"""
        return self.get_by_filters({'market': market})

    def get_tracking_stocks(self):
        """获取所有追踪的股票"""
        return self.get_by_filters({'tracking': True})

    def update_tracking_status(self, code: str, tracking: bool):
        """更新股票追踪状态"""
        stock = self.get_by_code(code)
        if stock:
            return self.update(stock.id, tracking=tracking)
        return None

    def upsert_by_code(self, code: str, **kwargs):
        """根据股票代码插入或更新股票信息"""
        return self.upsert('code', code, **kwargs)
