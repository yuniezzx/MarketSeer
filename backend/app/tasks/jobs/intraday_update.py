"""
分时数据更新任务
"""

from datetime import datetime
from app.utils.logger import get_logger
from app.utils.trading_calendar import is_trading_day
from app.utils.time_helper import get_current_time
from app.services.intraday_service import IntraDayDataService

logger = get_logger(__name__)

def is_trading_time() -> bool:
    """
    检查当前是否在交易时间内
    交易时间: 9:30-11:30, 13:00-15:00
    
    Returns:
        bool: True 表示在交易时间内，False 表示不在
    """
    now = datetime.now()
    current_time = now.time()
    
    # 上午交易时间: 9:30-11:30
    morning_start = datetime.strptime('09:30:00', '%H:%M:%S').time()
    morning_end = datetime.strptime('11:30:00', '%H:%M:%S').time()
    
    # 下午交易时间: 13:00-15:00
    afternoon_start = datetime.strptime('13:00:00', '%H:%M:%S').time()
    afternoon_end = datetime.strptime('15:00:00', '%H:%M:%S').time()
    
    # 判断是否在交易时间段内
    in_morning = morning_start <= current_time <= morning_end
    in_afternoon = afternoon_start <= current_time <= afternoon_end
    
    return in_morning or in_afternoon

def fetch_intraday_data(app):
    """定时任务：获取追踪股票的分时数据（仅在交易日和交易时间执行）"""
    with app.app_context():
        logger.info('=' * 50)
        logger.info('分时数据更新任务触发')
        logger.info('当前日期/时间：%s', get_current_time())

        # 检查是否为交易日
        if not is_trading_day():
            logger.info('今天不是交易日，跳过分时数据更新')
            logger.info('=' * 50)
            return

        # 检查是否在交易时间内
        if not is_trading_time():
            logger.info('当前不在交易时间内，跳过分时数据更新')
            logger.info('=' * 50)
            return

        logger.info('今天是交易日且在交易时间内，开始更新分时数据...')

        try:
            # 执行分时数据更新
            intraday_service = IntraDayDataService()
            result = intraday_service.fetch_and_save_intraday_data()
            logger.info(f'分时数据更新结果: {result}')

        except Exception as e:
            logger.error(f'分时数据更新失败: {str(e)}', exc_info=True)

        logger.info('=' * 50)
