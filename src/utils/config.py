"""
配置管理模块

负责加载和管理应用配置，支持YAML配置文件和环境变量。
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv


class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_file: str = "config/config.yaml", env_file: str = "config/.env"):
        """
        初始化配置管理器

        Args:
            config_file: YAML配置文件路径
            env_file: 环境变量文件路径
        """
        self.config_file = config_file
        self.env_file = env_file
        self._config = {}
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        # 加载环境变量
        self._load_env_file()

        # 加载YAML配置文件
        self._load_yaml_config()

        # 处理环境变量替换
        self._process_env_substitution()

    def _load_env_file(self) -> None:
        """加载.env文件"""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            print(f"已加载环境变量文件: {self.env_file}")
        else:
            print(f"环境变量文件不存在: {self.env_file}")

    def _load_yaml_config(self) -> None:
        """加载YAML配置文件"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as file:
                    self._config = yaml.safe_load(file) or {}
                print(f"已加载配置文件: {self.config_file}")
            else:
                raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._config = {}

    def _process_env_substitution(self) -> None:
        """处理配置中的环境变量替换"""
        self._config = self._substitute_env_vars(self._config)

    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        递归替换配置中的环境变量

        支持格式: ${ENV_VAR} 或 ${ENV_VAR:default_value}
        """
        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._replace_env_in_string(obj)
        else:
            return obj

    def _replace_env_in_string(self, text: str) -> str:
        """
        替换字符串中的环境变量

        Args:
            text: 包含环境变量的字符串

        Returns:
            替换后的字符串
        """
        # 匹配 ${VAR} 或 ${VAR:default} 格式
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

        def replace_match(match):
            env_var = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ''
            return os.getenv(env_var, default_value)

        return re.sub(pattern, replace_match, text)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键

        Args:
            key: 配置键，支持 'database.mysql.host' 格式
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_database_config(self, db_type: str = "mysql") -> Dict[str, Any]:
        """
        获取数据库配置

        Args:
            db_type: 数据库类型 (mysql, postgresql等)

        Returns:
            数据库配置字典
        """
        return self.get(f"database.{db_type}", {})

    def get_database_url(self, db_type: str = "mysql") -> str:
        """
        生成数据库连接URL

        Args:
            db_type: 数据库类型

        Returns:
            数据库连接URL
        """
        config = self.get_database_config(db_type)

        if not config:
            raise ValueError(f"未找到数据库配置: {db_type}")

        host = config.get('host', 'localhost')
        port = config.get('port', 3306)
        database = config.get('database', '')
        username = config.get('username', '')
        password = config.get('password', '')
        charset = config.get('charset', 'utf8mb4')

        if db_type == "mysql":
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset={charset}"
        elif db_type == "postgresql":
            return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get("logging", {})

    def get_data_source_config(self, source: str) -> Dict[str, Any]:
        """
        获取数据源配置

        Args:
            source: 数据源名称 (tushare, akshare, yfinance)

        Returns:
            数据源配置字典
        """
        return self.get(f"data_sources.{source}", {})

    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return self.get("app", {})

    def is_debug(self) -> bool:
        """判断是否为调试模式"""
        # 优先检查环境变量
        debug_env = os.getenv('DEBUG', '').lower()
        if debug_env in ('true', '1', 'yes', 'on'):
            return True
        elif debug_env in ('false', '0', 'no', 'off'):
            return False

        # 检查配置文件
        return self.get("app.debug", False)

    def get_env(self) -> str:
        """获取运行环境"""
        return os.getenv('APP_ENV', self.get("app.env", "development"))

    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        """支持 in 操作符"""
        return self.get(key) is not None


# 全局配置实例
config = ConfigManager()


def get_config() -> ConfigManager:
    """获取全局配置实例"""
    return config


def reload_config() -> None:
    """重新加载全局配置"""
    global config
    config.reload()


# 便捷函数
def get_database_url(db_type: str = "mysql") -> str:
    """获取数据库连接URL"""
    return config.get_database_url(db_type)


def get_database_config(db_type: str = "mysql") -> Dict[str, Any]:
    """获取数据库配置"""
    return config.get_database_config(db_type)


def is_debug() -> bool:
    """判断是否为调试模式"""
    return config.is_debug()


def get_env() -> str:
    """获取运行环境"""
    return config.get_env()
