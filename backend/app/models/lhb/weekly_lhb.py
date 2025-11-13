"""
龙虎榜周数据模型
"""

from ..base import BaseModel, db

class WeeklyLHB(BaseModel):
    """
    龙虎榜周数据表

    存储每周龙虎榜相关信息
    """

    __tablename__ = 'weekly_lhb'

    code = db.Column(db.String(20), nullable=False, index=True, comment='股票代码')
    name = db.Column(db.String(100), nullable=False, comment='股票名称')
    listed_date = db.Column(db.String(20), comment='上市日期')
    analysis = db.Column(db.Text, comment='分析')
    close_price = db.Column(db.Float, comment='收盘价')
    change_percent = db.Column(db.Float, comment='涨跌幅(%)')
    turnover_rate = db.Column(db.Float, comment='换手率(%)')

    __table_args__ = (
        db.Index('idx_code', 'code'),
    )

    def __repr__(self):
        return f'<WeeklyLHB {self.code} - {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'listed_date': self.listed_date,
            'analysis': self.analysis,
            'close_price': self.close_price,
            'change_percent': self.change_percent,
            'turnover_rate': self.turnover_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_dict(data):
        return WeeklyLHB(
            code=data.get('code'),
            name=data.get('name'),
            listed_date=data.get('listed_date'),
            analysis=data.get('analysis'),
            close_price=data.get('close_price'),
            change_percent=data.get('change_percent'),
            turnover_rate=data.get('turnover_rate'),
        )
