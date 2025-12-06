from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True  # 标记为抽象类，不创建实际表

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间'
    )


def init_db():
    """初始化数据库表"""
    from config import Config, DATA_DIR
    from logger import logger

    config = Config()
    if config.ENV == 'development':
        # 确保 data 目录存在
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    db.create_all()
    logger.info("数据库表初始化完成")
