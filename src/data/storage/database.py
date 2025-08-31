"""
数据库管理模块

提供MySQL数据库连接、操作和管理功能。
"""

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from datetime import datetime
import pandas as pd

from ...utils.config import get_config
from ...utils.logger import get_database_logger, log_database_operation, log_db_connection, log_db_error

# 数据库基础模型
Base = declarative_base()


class DatabaseManager:
    """数据库管理器类"""

    def __init__(self, db_type: str = "mysql"):
        """
        初始化数据库管理器

        Args:
            db_type: 数据库类型，默认为mysql
        """
        self.db_type = db_type
        self.config = get_config()
        self.logger = get_database_logger()
        self.engine = None
        self.SessionLocal = None
        self.metadata = MetaData()
        self._setup_database()

    def _setup_database(self) -> None:
        """设置数据库连接"""
        try:
            # 获取数据库配置
            db_config = self.config.get_database_config(self.db_type)
            if not db_config:
                raise ValueError(f"未找到数据库配置: {self.db_type}")

            # 构建连接URL
            database_url = self.config.get_database_url(self.db_type)

            # 获取连接池配置
            pool_config = db_config.get('pool', {})
            connect_args = db_config.get('connect_args', {})

            # 创建数据库引擎
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=pool_config.get('pool_size', 10),
                max_overflow=pool_config.get('max_overflow', 20),
                pool_timeout=pool_config.get('pool_timeout', 30),
                pool_recycle=pool_config.get('pool_recycle', 3600),
                pool_pre_ping=pool_config.get('pool_pre_ping', True),
                connect_args=connect_args,
                echo=self.config.is_debug(),  # 调试模式下显示SQL语句
            )

            # 创建会话工厂
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # 测试连接
            self._test_connection()

            host = db_config.get('host', 'unknown')
            log_db_connection('connected', host)
            self.logger.info(f"数据库连接成功: {self.db_type}@{host}")

        except Exception as e:
            log_db_error(str(e), 'connection_setup')
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    def _test_connection(self) -> None:
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            raise ConnectionError(f"数据库连接测试失败: {str(e)}")

    @contextmanager
    def get_session(self):
        """
        获取数据库会话上下文管理器

        Returns:
            数据库会话
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            log_db_error(str(e), 'session_operation')
            raise
        finally:
            session.close()

    @log_database_operation("执行SQL查询")
    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                # 将结果转换为字典列表
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except SQLAlchemyError as e:
            log_db_error(str(e), 'execute_query')
            raise

    @log_database_operation("执行SQL命令")
    def execute_command(self, command: str, params: Dict = None) -> int:
        """
        执行SQL命令（INSERT, UPDATE, DELETE等）

        Args:
            command: SQL命令
            params: 命令参数

        Returns:
            受影响的行数
        """
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    result = conn.execute(text(command), params or {})
                    return result.rowcount
        except SQLAlchemyError as e:
            log_db_error(str(e), 'execute_command')
            raise

    @log_database_operation("批量执行SQL命令")
    def execute_batch(self, command: str, params_list: List[Dict]) -> int:
        """
        批量执行SQL命令

        Args:
            command: SQL命令
            params_list: 参数列表

        Returns:
            总受影响行数
        """
        try:
            total_affected = 0
            with self.engine.connect() as conn:
                with conn.begin():
                    for params in params_list:
                        result = conn.execute(text(command), params)
                        total_affected += result.rowcount
            return total_affected
        except SQLAlchemyError as e:
            log_db_error(str(e), 'execute_batch')
            raise

    def read_dataframe(self, query: str, params: Dict = None) -> pd.DataFrame:
        """
        执行查询并返回DataFrame

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            pandas DataFrame
        """
        try:
            return pd.read_sql(query, self.engine, params=params)
        except Exception as e:
            log_db_error(str(e), 'read_dataframe')
            raise

    @log_database_operation("保存DataFrame到数据库")
    def save_dataframe(
        self, df: pd.DataFrame, table_name: str, if_exists: str = 'append', index: bool = False, **kwargs
    ) -> None:
        """
        将DataFrame保存到数据库

        Args:
            df: pandas DataFrame
            table_name: 表名
            if_exists: 如果表存在的处理方式 ('fail', 'replace', 'append')
            index: 是否保存索引
            **kwargs: 其他参数
        """
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=index, **kwargs)
            self.logger.info(f"成功保存 {len(df)} 行数据到表 {table_name}")
        except Exception as e:
            log_db_error(str(e), f'save_dataframe_to_{table_name}')
            raise

    def create_table(self, table_name: str, columns: Dict[str, Any]) -> None:
        """
        创建数据表

        Args:
            table_name: 表名
            columns: 列定义字典，格式: {'column_name': column_type}
        """
        try:
            # 构建列定义
            table_columns = []
            for col_name, col_type in columns.items():
                if col_name.lower() == 'id' and col_type == 'primary_key':
                    table_columns.append(Column('id', Integer, primary_key=True, autoincrement=True))
                elif col_type == 'string':
                    table_columns.append(Column(col_name, String(255)))
                elif col_type == 'text':
                    table_columns.append(Column(col_name, Text))
                elif col_type == 'integer':
                    table_columns.append(Column(col_name, Integer))
                elif col_type == 'float':
                    table_columns.append(Column(col_name, Float))
                elif col_type == 'datetime':
                    table_columns.append(Column(col_name, DateTime, default=datetime.utcnow))
                else:
                    # 默认为字符串类型
                    table_columns.append(Column(col_name, String(255)))

            # 创建表对象
            table = Table(table_name, self.metadata, *table_columns)

            # 创建表
            table.create(self.engine, checkfirst=True)
            self.logger.info(f"成功创建表: {table_name}")

        except Exception as e:
            log_db_error(str(e), f'create_table_{table_name}')
            raise

    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在

        Args:
            table_name: 表名

        Returns:
            表是否存在
        """
        try:
            return self.engine.dialect.has_table(self.engine, table_name)
        except Exception as e:
            log_db_error(str(e), f'check_table_exists_{table_name}')
            return False

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表信息

        Args:
            table_name: 表名

        Returns:
            表信息字典
        """
        try:
            # 反射表结构
            table = Table(table_name, MetaData(), autoload_with=self.engine)

            columns_info = []
            for column in table.columns:
                columns_info.append(
                    {
                        'name': column.name,
                        'type': str(column.type),
                        'nullable': column.nullable,
                        'primary_key': column.primary_key,
                        'default': str(column.default) if column.default else None,
                    }
                )

            return {'table_name': table_name, 'columns': columns_info, 'column_count': len(columns_info)}
        except Exception as e:
            log_db_error(str(e), f'get_table_info_{table_name}')
            raise

    def get_connection_info(self) -> Dict[str, Any]:
        """
        获取数据库连接信息

        Returns:
            连接信息字典
        """
        try:
            db_config = self.config.get_database_config(self.db_type)
            pool_config = db_config.get('pool', {})

            # 获取连接池状态
            pool = self.engine.pool

            return {
                'database_type': self.db_type,
                'host': db_config.get('host'),
                'port': db_config.get('port'),
                'database': db_config.get('database'),
                'pool_size': pool_config.get('pool_size', 10),
                'pool_checked_out': pool.checkedout(),
                'pool_overflow': pool.overflow(),
                'pool_checked_in': pool.checkedin(),
            }
        except Exception as e:
            log_db_error(str(e), 'get_connection_info')
            raise

    def close_connection(self) -> None:
        """关闭数据库连接"""
        try:
            if self.engine:
                self.engine.dispose()
                self.logger.info("数据库连接已关闭")
                log_db_connection('disconnected')
        except Exception as e:
            log_db_error(str(e), 'close_connection')

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close_connection()


# 全局数据库管理器实例
_db_manager = None


def get_database() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def close_database() -> None:
    """关闭全局数据库连接"""
    global _db_manager
    if _db_manager:
        _db_manager.close_connection()
        _db_manager = None


# 便捷函数
def execute_query(query: str, params: Dict = None) -> List[Dict]:
    """执行SQL查询"""
    return get_database().execute_query(query, params)


def execute_command(command: str, params: Dict = None) -> int:
    """执行SQL命令"""
    return get_database().execute_command(command, params)


def read_sql(query: str, params: Dict = None) -> pd.DataFrame:
    """读取SQL查询结果为DataFrame"""
    return get_database().read_dataframe(query, params)


def save_to_sql(df: pd.DataFrame, table_name: str, if_exists: str = 'append', **kwargs) -> None:
    """保存DataFrame到SQL表"""
    return get_database().save_dataframe(df, table_name, if_exists, **kwargs)


@contextmanager
def database_session():
    """数据库会话上下文管理器"""
    db = get_database()
    with db.get_session() as session:
        yield session
