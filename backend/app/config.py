"""
MarketSeer 全局配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


# 基础路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'


class Config:
    """应用配置类"""

    # Flask 配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI',
        f'sqlite:///{DATA_DIR / "marketseer.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API 配置
    API_VERSION = 'v1'

    # 数据源配置
    DATA_SOURCES = {
        'akshare': {'enabled': True, 'priority': 1},
        'efinance': {'enabled': True, 'priority': 2},
        'yfinance': {'enabled': False, 'priority': 3},
    }

    # 数据更新配置
    UPDATE_INTERVAL = 3600  # 秒

    # 定时任务调度器配置
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    SCHEDULER_JOB_DEFAULTS = {'coalesce': False, 'max_instances': 1}

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = BASE_DIR / 'logs' / 'marketseer.log'

    # CORS 配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'http://localhost:5000']


class DevelopmentConfig(Config):
    """开发环境配置"""

    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""

    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置 SECRET_KEY 环境变量")


class TestingConfig(Config):
    """测试环境配置"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
