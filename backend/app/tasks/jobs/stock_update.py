"""
股票数据定时更新任务
"""
from app.services.stock_service import StockInfoService
from app.utils.trading_calendar import is_trading_day
from flask import current_app

def update_stock_data():
    """定时任务：更新股票数据"""
    with current_app.app_context():
        if is_trading_day():
            service = StockInfoService()
            # 可根据实际需求调整数据源和参数
            service.add_stock_by_code("000001")  # 示例：更新指定股票
            # 可扩展为批量更新
