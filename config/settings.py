"""
主配置文件

包含项目的核心配置设置
"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """主配置类"""

    # 基础配置
    PROJECT_NAME = "MarketSeer"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # 数据相关配置
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    EXPORTS_DATA_DIR = DATA_DIR / "exports"

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = BASE_DIR / "logs"
    LOG_FILE = LOG_DIR / "marketseer.log"

    # API配置
    AKSHARE_TIMEOUT = int(os.getenv("AKSHARE_TIMEOUT", "30"))
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.1"))  # 请求间隔，避免频率限制

    # 缓存配置
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    CACHE_EXPIRE_HOURS = int(os.getenv("CACHE_EXPIRE_HOURS", "24"))

    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """获取所有配置"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }


# 全局配置实例
settings = Settings()
