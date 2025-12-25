from flask import Flask
from flask_cors import CORS
from config import Config
from logger import logger


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 启用 CORS
    CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})

    # 初始化数据库
    from app.models import db, init_db
    from flask_migrate import Migrate

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        init_db()

    # 注册蓝图
    from app.routes import stocks_bp, dragon_tiger_bp

    app.register_blueprint(stocks_bp)
    app.register_blueprint(dragon_tiger_bp)

    # 初始化调度器（仅在主进程中初始化，避免 debug 模式重复执行）
    import os

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.config.get("FLASK_DEBUG"):
        from app.scheduler import init_scheduler

        init_scheduler(app)
        logger.info("定时任务调度器已集成到 Flask 应用")

    return app
