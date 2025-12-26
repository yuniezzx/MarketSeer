"""
每日行情数据采集定时任务

负责定时采集每日股票行情数据
"""

from datetime import datetime
from logger import logger
from app.services import MarketQuoteService
from app.utils.timer import is_trading_day


def collect_daily_market_quote(app):
    """
    采集每日行情数据

    在交易日下午4点30分执行,采集当日全部股票的行情数据

    Args:
        app: Flask 应用实例
    """
    with app.app_context():
        # 检查是否为交易日
        if not is_trading_day():
            logger.info("今天不是交易日，跳过每日行情数据采集")
            return

        try:
            logger.info("=" * 60)
            logger.info("开始采集每日行情数据")
            logger.info("=" * 60)

            # 创建服务实例
            service = MarketQuoteService()

            # 执行每日更新
            success = service.daily_update()

            if success:
                logger.info("=" * 60)
                logger.info("每日行情数据采集完成")
                logger.info("=" * 60)
            else:
                logger.error("=" * 60)
                logger.error("每日行情数据采集失败")
                logger.error("=" * 60)

        except Exception as e:
            logger.error(f"每日行情数据采集过程中发生异常: {e}", exc_info=True)


def register_jobs(scheduler, app):
    """
    注册每日行情数据采集任务

    Args:
        scheduler: APScheduler 调度器实例
        app: Flask 应用实例
    """
    scheduler.add_job(
        func=collect_daily_market_quote,
        trigger="cron",
        args=[app],
        id="collect_daily_market_quote",
        name="采集每日行情数据",
        hour=16,  # 下午4点
        minute=30,  # 30分
        replace_existing=True,
    )

    logger.info("已注册定时任务: 采集每日行情数据 (每天下午4点30分)")
