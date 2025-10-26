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

    return app
