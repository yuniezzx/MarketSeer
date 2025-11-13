"""
MarketSeer Flask Application Factory
"""

from flask import Flask
from flask_cors import CORS
from app.config import Config


def create_app(config_class=Config):
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 启用 CORS
    CORS(app)

    # 初始化数据库
    from app.models import db, init_db

    db.init_app(app)

    with app.app_context():
        init_db()

    # 注册蓝图
    from app.routes import api_bp

    app.register_blueprint(api_bp, url_prefix='/api')

    # 初始化定时任务调度器
    import os
    from app.tasks.scheduler import scheduler, start_scheduler
    from app.utils.logger import get_logger

    logger = get_logger(__name__)

    # 只在主进程或非 debug 模式下启动 scheduler（避免 Flask reloader 重复启动）
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        scheduler.configure(timezone=app.config.get("SCHEDULER_TIMEZONE", "Asia/Shanghai"))
        start_scheduler()

        from app.tasks.jobs.daily_update import daily_update_stock_data

        # 添加定时任务，使用 cron 触发器（每天晚上 8 点执行）
        scheduler.add_job(
            lambda: daily_update_stock_data(app),
            trigger="cron",
            hour=20,  # 每天晚上 8 点
            minute=0,  # 0 分
            second=0,  # 0 秒
            id="daily_update_stock_data",
            replace_existing=True,
        )

        logger.info("调度器已启动，任务将在每天 20:00 执行")
        logger.info(f"已添加任务: {[job.id for job in scheduler.get_jobs()]}")

        # 立即执行一次任务用于测试
        logger.info("立即执行一次定时任务进行测试...")
        try:
            daily_update_stock_data(app)
        except Exception as e:
            logger.error(f"测试任务执行失败: {str(e)}", exc_info=True)
    else:
        logger.info("跳过调度器初始化（Flask reloader 副进程）")

    return app
