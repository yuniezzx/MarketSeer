"""
基础模型类定义
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BaseModel(db.Model):
    """
    所有业务模型的抽象基类
    
    提供通用字段和方法：
    - id: 主键
    - created_at: 创建时间
    - updated_at: 更新时间
    - to_dict(): 转换为字典
    - save(): 保存到数据库
    - delete(): 从数据库删除
    """
    
    __abstract__ = True  # 标记为抽象类，不创建实际表
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    def to_dict(self):
        """
        将模型转换为字典格式
        子类可以覆盖此方法以自定义输出
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # 处理日期时间类型
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def save(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """从数据库删除"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """根据 ID 查询"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls, limit=None):
        """查询所有记录"""
        query = cls.query
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def count(cls):
        """统计记录数"""
        return cls.query.count()
    
    def __repr__(self):
        """对象的字符串表示"""
        return f'<{self.__class__.__name__} {self.id}>'


def init_db():
    """
    初始化数据库
    
    功能：
    - 确保 data 目录存在
    - 创建所有表结构
    """
    from app.config import DATA_DIR
    
    # 确保 data 目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建所有表
    db.create_all()
    print("数据库初始化完成")
