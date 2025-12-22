from loguru import logger
import sys
from pathlib import Path
from config import Config

# 配置 logger
config = Config()

# 确保日志目录存在
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# 移除默认处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if config.FLASK_DEBUG else "INFO",
    colorize=True,
    backtrace=True,  # 显示异常的完整堆栈
    diagnose=True,  # 显示变量值
)

# 添加常规日志文件输出
logger.add(
    log_dir / "app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    level="DEBUG" if config.FLASK_DEBUG else "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {process}:{thread} | {name}:{function}:{line} - {message}",
    backtrace=True,
    diagnose=config.FLASK_DEBUG,  # 只在 DEBUG 模式显示变量值
)

# 添加错误日志单独文件
logger.add(
    log_dir / "error_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="90 days",  # 错误日志保留更久
    compression="zip",
    encoding="utf-8",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {process}:{thread} | {name}:{function}:{line} - {message}",
    backtrace=True,
    diagnose=True,
)
