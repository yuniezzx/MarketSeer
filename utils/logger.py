import os
from loguru import logger

def get_data_sources_logger(name: str):
    # 读取环境变量中的日志等级，默认 INFO
    level = os.getenv("DATA_CLIENT_LOG_LEVEL", "INFO").upper()

    # 先移除默认的 handler（避免重复添加）
    logger.remove()

    # 添加一个新的 sink（这里输出到 stdout）
    logger.add(
        sink=lambda msg: print(msg, end=""),  # stdout
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "{extra[name]} | "   # 用 extra 保存自定义 name
               "<cyan>{message}</cyan>"
    )

    # 绑定额外字段 name
    return logger.bind(name=name)
