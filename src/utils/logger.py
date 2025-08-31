"""
日志管理模块

使用loguru提供统一的日志管理功能。
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from .config import get_config


class LoggerManager:
    """日志管理器类"""

    def __init__(self):
        """初始化日志管理器"""
        self._initialized = False
        self.setup_logger()

    def setup_logger(self) -> None:
        """设置日志配置"""
        if self._initialized:
            return

        config = get_config()
        log_config = config.get_logging_config()

        # 移除默认的控制台处理器
        logger.remove()

        # 获取日志配置
        level = log_config.get('level', 'INFO')
        format_str = log_config.get(
            'format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}'
        )

        # 添加控制台输出
        logger.add(sys.stdout, level=level, format=format_str, colorize=True, backtrace=True, diagnose=True)

        # 添加文件输出
        self._setup_file_handlers(log_config)

        self._initialized = True
        logger.info("日志系统初始化完成")

    def _setup_file_handlers(self, log_config: dict) -> None:
        """设置文件日志处理器"""
        files_config = log_config.get('files', {})
        rotation_config = log_config.get('rotation', {})

        # 确保日志目录存在
        self._ensure_log_directory()

        # 应用日志
        app_log = files_config.get('app_log', 'logs/app.log')
        if app_log:
            logger.add(
                app_log,
                level='DEBUG',
                format=log_config.get('format'),
                rotation=rotation_config.get('size', '100 MB'),
                retention=rotation_config.get('retention', '30 days'),
                compression='zip',
                backtrace=True,
                diagnose=True,
            )

        # 错误日志
        error_log = files_config.get('error_log', 'logs/error.log')
        if error_log:
            logger.add(
                error_log,
                level='ERROR',
                format=log_config.get('format'),
                rotation=rotation_config.get('size', '100 MB'),
                retention=rotation_config.get('retention', '30 days'),
                compression='zip',
                backtrace=True,
                diagnose=True,
            )

        # 数据库日志
        db_log = files_config.get('db_log', 'logs/database.log')
        if db_log:
            logger.add(
                db_log,
                level='INFO',
                format=log_config.get('format'),
                rotation=rotation_config.get('size', '100 MB'),
                retention=rotation_config.get('retention', '30 days'),
                compression='zip',
                filter=lambda record: 'database' in record.get('extra', {}),
                backtrace=True,
                diagnose=True,
            )

    def _ensure_log_directory(self) -> None:
        """确保日志目录存在"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

    def get_logger(self, name: Optional[str] = None):
        """
        获取日志器

        Args:
            name: 日志器名称

        Returns:
            日志器实例
        """
        if not self._initialized:
            self.setup_logger()

        if name:
            return logger.bind(name=name)
        return logger

    def get_database_logger(self):
        """获取数据库专用日志器"""
        return logger.bind(database=True)


# 全局日志管理器实例
_logger_manager = LoggerManager()


def get_logger(name: Optional[str] = None):
    """
    获取日志器

    Args:
        name: 日志器名称

    Returns:
        日志器实例
    """
    return _logger_manager.get_logger(name)


def get_database_logger():
    """获取数据库专用日志器"""
    return _logger_manager.get_database_logger()


def setup_logger() -> None:
    """重新设置日志配置"""
    global _logger_manager
    _logger_manager._initialized = False
    _logger_manager.setup_logger()


# 便捷的日志函数
def log_debug(message: str, **kwargs) -> None:
    """记录调试日志"""
    logger.debug(message, **kwargs)


def log_info(message: str, **kwargs) -> None:
    """记录信息日志"""
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """记录警告日志"""
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs) -> None:
    """记录错误日志"""
    logger.error(message, **kwargs)


def log_critical(message: str, **kwargs) -> None:
    """记录严重错误日志"""
    logger.critical(message, **kwargs)


def log_exception(message: str, **kwargs) -> None:
    """记录异常日志"""
    logger.exception(message, **kwargs)


# 数据库相关日志函数
def log_db_operation(operation: str, table: str = None, **kwargs) -> None:
    """
    记录数据库操作日志

    Args:
        operation: 操作类型 (SELECT, INSERT, UPDATE, DELETE等)
        table: 表名
        **kwargs: 其他参数
    """
    db_logger = get_database_logger()
    message = f"数据库操作: {operation}"
    if table:
        message += f" - 表: {table}"
    db_logger.info(message, **kwargs)


def log_db_error(error: str, operation: str = None, **kwargs) -> None:
    """
    记录数据库错误日志

    Args:
        error: 错误信息
        operation: 操作类型
        **kwargs: 其他参数
    """
    db_logger = get_database_logger()
    message = f"数据库错误: {error}"
    if operation:
        message += f" - 操作: {operation}"
    db_logger.error(message, **kwargs)


def log_db_connection(status: str, host: str = None, **kwargs) -> None:
    """
    记录数据库连接日志

    Args:
        status: 连接状态 (connected, disconnected, failed等)
        host: 数据库主机
        **kwargs: 其他参数
    """
    db_logger = get_database_logger()
    message = f"数据库连接: {status}"
    if host:
        message += f" - 主机: {host}"
    db_logger.info(message, **kwargs)


# 装饰器函数
def log_function_call(func_name: str = None):
    """
    日志装饰器，记录函数调用

    Args:
        func_name: 自定义函数名称
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            name = func_name or func.__name__
            logger.debug(f"调用函数: {name}, args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"函数 {name} 执行成功")
                return result
            except Exception as e:
                logger.error(f"函数 {name} 执行失败: {str(e)}")
                raise

        return wrapper

    return decorator


def log_database_operation(operation: str = None):
    """
    数据库操作装饰器

    Args:
        operation: 操作类型描述
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__
            db_logger = get_database_logger()
            db_logger.info(f"开始数据库操作: {op_name}")
            try:
                result = func(*args, **kwargs)
                db_logger.info(f"数据库操作成功: {op_name}")
                return result
            except Exception as e:
                db_logger.error(f"数据库操作失败: {op_name} - 错误: {str(e)}")
                raise

        return wrapper

    return decorator


# 初始化日志系统
setup_logger()
