"""
股票数据日常更新任务
"""

from app.utils.logger import get_logger
from app.services.stock_service import StockInfoService
from app.utils.trading_calendar import is_trading_day
from app.utils.time_helper import get_current_time

logger = get_logger(__name__)


def daily_update_stock_data(app):
    """定时任务：更新股票数据（仅在交易日执行）"""
    with app.app_context():
        logger.info('=' * 50)
        logger.info('定时任务触发')
        logger.info('当前日期/时间：%s', get_current_time())

        # 检查是否为交易日
        if not is_trading_day():
            logger.info('今天不是交易日，跳过数据更新')
            logger.info('=' * 50)
            return

        logger.info('今天是交易日，开始更新股票数据...')

        try:
            # TODO: 这里添加实际的数据更新逻辑
            # stock_service = StockInfoService()
            # result = stock_service.update_all_stocks()
            logger.info('股票数据更新完成')
        except Exception as e:
            logger.error(f'股票数据更新失败: {str(e)}', exc_info=True)

        logger.info('=' * 50)
