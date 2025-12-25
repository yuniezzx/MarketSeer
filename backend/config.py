"""
MarketSeer 全局配置
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()  # 确保在导入 os 之前加载 .env 环境变量


# 基础路径
BASE_DIR = Path(__file__).parent  # 指向 /backend
DATA_DIR = BASE_DIR / "data"


class Config:
    """应用配置类"""

    ENV = os.environ.get("ENV", "development")  # development, production

    # Flask 配置
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))

    # 数据库配置
    if ENV == "production":
        SQLALCHEMY_DATABASE_URI = os.getenv("SUPABASE_URI")  # 云端 DB
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'data' / 'marketseer.db'}"

    # 定时任务调度器配置
    SCHEDULER_API_ENABLED = os.getenv("SCHEDULER_API_ENABLED", "true").lower() == "true"
    SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Asia/Shanghai")
    SCHEDULER_JOB_DEFAULTS = json.loads(
        os.getenv("SCHEDULER_JOB_DEFAULTS", '{"coalesce": false, "max_instances": 1}')
    )

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE = BASE_DIR / "logs" / "marketseer.log"

    # AkShare 数据保存配置
    SAVE_RAW_DATA = os.getenv("SAVE_RAW_DATA", "true").lower() == "true"
    SAVE_RAW_DATA_DAYS = int(os.getenv("SAVE_RAW_DATA_DAYS", 30))
    AKSHARE_RAW_DATA_DIR = DATA_DIR / "akshare_raw"

    # CORS 配置
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:5173,http://localhost:5000"
    ).split(",")
