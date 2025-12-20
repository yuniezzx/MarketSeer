"""
龙虎榜数据采集定时任务

负责定期采集和更新龙虎榜数据
"""

from logger import logger
from app.utils.timer import is_trading_day


def collect_daily_dragon_tiger(app):
    """
    采集每日龙虎榜数据

    在每个交易日收盘后执行，采集当天的龙虎榜数据

    Args:
        app: Flask 应用实例
    """
    with app.app_context():
        try:
            # 检查是否为交易日
            if not is_trading_day():
                logger.info("今天不是交易日，跳过龙虎榜数据采集")
                return

            logger.info("=" * 60)
            logger.info("开始采集每日龙虎榜数据...")
            logger.info("=" * 60)

            # TODO: 实现具体的数据采集逻辑
            # 1. 调用数据源获取龙虎榜数据
            # 2. 数据清洗和转换
            # 3. 保存到数据库

            logger.info("每日龙虎榜数据采集完成")

        except Exception as e:
            logger.exception(f"采集每日龙虎榜数据失败: {e}")


def register_jobs(scheduler, app):
    """
    注册龙虎榜相关的定时任务

    Args:
        scheduler: APScheduler 调度器实例
        app: Flask 应用实例
    """
    # 每日龙虎榜数据采集任务
    # 每个交易日 20:00 执行
    scheduler.add_job(
        func=collect_daily_dragon_tiger,
        trigger="cron",
        args=[app],
        id="collect_daily_dragon_tiger",
        name="采集每日龙虎榜数据",
        hour=20,
        minute=0,
        replace_existing=True,
    )
    logger.info("已注册任务: 采集每日龙虎榜数据 (每天 20:00)")
