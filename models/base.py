"""
基础模型类

包含所有数据模型的通用字段和方法
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """基础模型类"""

    __abstract__ = True

    # 通用时间戳字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间"
    )
    is_active = Column(Boolean, default=True, nullable=False, comment="是否有效")

    def to_dict(self):
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def __repr__(self):
        """字符串表示"""
        return f"<{self.__class__.__name__}({self.to_dict()})>"

    @classmethod
    def get_table_name(cls):
        """获取表名"""
        return cls.__tablename__

    @classmethod
    def get_columns(cls):
        """获取所有列名"""
        return [column.name for column in cls.__table__.columns]
