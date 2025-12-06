from .base_service import BaseService


class StocksService(BaseService):
    def __init__(self):
        super().__init__()

    @staticmethod
    def add_stock(symbol: str):
        # Placeholder for adding a stock
        return {'code': '002156', 'name': '通富微电'}
