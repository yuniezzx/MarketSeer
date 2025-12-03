"""
分时数据模型
"""
from app.models.base import db, BaseModel


class IntraDayData(BaseModel):
    """
    分时数据表
    
    存储股票的分时交易数据
    """
    __tablename__ = 'intraday_data'
    
    stock_code = db.Column(db.String(20), nullable=False, index=True, comment='股票代码')
    date = db.Column(db.DateTime, nullable=False, index=True, comment='交易日期')
    trade_time = db.Column(db.DateTime, nullable=False, index=True, comment='交易时间')
    price = db.Column(db.Float, nullable=False, comment='成交价')
    volume = db.Column(db.BigInteger, comment='手数')
    trade_type = db.Column(db.String(20), comment='成交类型（买入/卖出）')
    
    __table_args__ = (
        db.Index('idx_stock_time', 'stock_code', 'trade_time'),
        db.UniqueConstraint('stock_code', 'trade_time', name='uq_stock_time'),
    )
    
    def __repr__(self):
        return f'<IntraDayData {self.stock_code} {self.trade_time}>'
