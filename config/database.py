"""
数据库配置文件

包含数据库连接和配置相关设置
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class DatabaseConfig:
    """数据库配置类"""

    # 数据库连接配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "marketseer")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

    # SQLite配置（默认使用SQLite）
    SQLITE_PATH = os.getenv("SQLITE_PATH", "data/marketseer.db")

    # 连接池配置
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

    @classmethod
    def get_mysql_url(cls) -> str:
        """获取MySQL连接URL"""
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}?charset={cls.DB_CHARSET}"

    @classmethod
    def get_postgresql_url(cls) -> str:
        """获取PostgreSQL连接URL"""
        return (
            f"postgresql+psycopg2://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    @classmethod
    def get_sqlite_url(cls) -> str:
        """获取SQLite连接URL"""
        return f"sqlite:///{cls.SQLITE_PATH}"

    @classmethod
    def get_database_url(cls) -> str:
        """根据环境变量获取数据库连接URL"""
        db_type = os.getenv("DB_TYPE", "sqlite").lower()

        if db_type == "mysql":
            return cls.get_mysql_url()
        elif db_type == "postgresql":
            return cls.get_postgresql_url()
        else:
            return cls.get_sqlite_url()


# 数据库引擎配置
def create_database_engine():
    """创建数据库引擎"""
    database_url = DatabaseConfig.get_database_url()

    engine_kwargs = {
        "pool_size": DatabaseConfig.POOL_SIZE,
        "max_overflow": DatabaseConfig.MAX_OVERFLOW,
        "pool_timeout": DatabaseConfig.POOL_TIMEOUT,
        "pool_recycle": DatabaseConfig.POOL_RECYCLE,
        "echo": os.getenv("DB_ECHO", "False").lower() == "true",
    }

    # SQLite不支持连接池参数
    if "sqlite" in database_url:
        engine_kwargs = {"echo": engine_kwargs["echo"]}

    return create_engine(database_url, **engine_kwargs)


# 全局数据库对象
Base = declarative_base()
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
