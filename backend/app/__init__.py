from flask import Flask
from flask_cors import CORS
from config import Config
from logger import logger


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 启用 CORS
    CORS(app)

    # 初始化数据库
    from app.models import db, init_db
    from flask_migrate import Migrate

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        init_db()

    # 注册蓝图
    from app.routes import stocks_bp

    app.register_blueprint(stocks_bp)

    return app
