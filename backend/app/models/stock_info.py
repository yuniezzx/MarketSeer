"""
股票基础信息模型
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class StockInfo(db.Model):
    """股票基础信息表"""
    
    __tablename__ = 'stock_info'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键')
    code = db.Column(db.String(20), unique=True, nullable=False, index=True, comment='股票代码')
    name = db.Column(db.String(100), nullable=False, comment='股票名称')
    market = db.Column(db.String(20), comment='市场（SH/SZ等）')
    industry = db.Column(db.String(50), comment='行业分类')
    list_date = db.Column(db.String(20), comment='上市日期')
    update_time = db.Column(db.String(30), default=lambda: datetime.now().isoformat(), comment='最后更新时间')
    
    def __repr__(self):
        return f'<StockInfo {self.code} - {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'market': self.market,
            'industry': self.industry,
            'list_date': self.list_date,
            'update_time': self.update_time
        }
    
    @staticmethod
    def from_dict(data):
        """从字典创建实例"""
        return StockInfo(
            code=data.get('code'),
            name=data.get('name'),
            market=data.get('market'),
            industry=data.get('industry'),
            list_date=data.get('list_date'),
            status=data.get('status', '上市'),
            source=data.get('source'),
            update_time=data.get('update_time', datetime.now().isoformat())
        )


def init_db():
    """初始化数据库"""
    from app.config import DATA_DIR
    
    # 确保 data 目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建所有表
    db.create_all()
    print("数据库初始化完成")
