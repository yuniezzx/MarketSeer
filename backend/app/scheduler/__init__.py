"""
APScheduler 定时任务调度器模块

负责管理和调度所有定时任务，与 Flask 应用集成
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from logger import logger

# 全局调度器实例
scheduler = None


def init_scheduler(app):
    """
    初始化并启动调度器

    Args:
        app: Flask 应用实例

    Returns:
        scheduler: APScheduler 调度器实例
    """
    global scheduler

    # 防止重复初始化
    if scheduler is not None:
        logger.warning("调度器已经初始化，跳过重复初始化")
        return scheduler

    # 获取配置
    timezone = app.config.get("SCHEDULER_TIMEZONE", "Asia/Shanghai")
    job_defaults = app.config.get("SCHEDULER_JOB_DEFAULTS", {"coalesce": False, "max_instances": 1})

    # 配置调度器
    jobstores = {"default": MemoryJobStore()}

    executors = {"default": ThreadPoolExecutor(max_workers=10)}

    # 创建调度器实例
    scheduler = BackgroundScheduler(
        jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=timezone
    )

    # 注册任务
    _register_jobs(app)

    # 启动调度器
    if not scheduler.running:
        scheduler.start()
        logger.info("=" * 60)
        logger.info("APScheduler 调度器已启动")
        logger.info(f"时区: {timezone}")
        logger.info(f"已注册任务数: {len(scheduler.get_jobs())}")
        logger.info("=" * 60)

    return scheduler


def _register_jobs(app):
    """
    注册所有定时任务

    Args:
        app: Flask 应用实例
    """
    from .jobs import dragon_tiger, market_quote

    # 注册龙虎榜数据采集任务
    dragon_tiger.register_jobs(scheduler, app)

    # 注册每日行情数据采集任务
    market_quote.register_jobs(scheduler, app)

    logger.info("所有定时任务已注册")

    # 🧪 测试：立即执行一次每日行情数据采集任务
    # logger.info("=" * 60)
    # logger.info("🧪 测试：立即执行一次每日行情数据采集任务")
    # logger.info("=" * 60)
    # market_quote.collect_daily_market_quote(app)


def shutdown_scheduler():
    """关闭调度器"""
    global scheduler

    if scheduler is not None and scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler 调度器已关闭")
        scheduler = None


def get_scheduler():
    """
    获取调度器实例

    Returns:
        scheduler: APScheduler 调度器实例
    """
    return scheduler


__all__ = ["init_scheduler", "shutdown_scheduler", "get_scheduler", "scheduler"]
