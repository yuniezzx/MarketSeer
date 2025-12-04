from .base import BaseModel, db


class DailyLHB(BaseModel):
    """
    龙虎榜周数据表

    存储每周龙虎榜相关信息
    """

    __tablename__ = 'daily_lhb'

    # 基本信息
    code = db.Column(db.String(20), nullable=False, index=True, comment='股票代码')
    name = db.Column(db.String(100), nullable=False, comment='股票名称')
    listed_date = db.Column(db.String(20), comment='上榜日期')

    # 股票数据
    close_price = db.Column(db.Float, comment='收盘价')
    change_percent = db.Column(db.Float, comment='涨跌幅(%)')
    turnover_rate = db.Column(db.Float, comment='换手率(%)')
    circulating_market_cap = db.Column(db.Float, comment='流通市值(亿元)')

    # 龙虎数据
    lhb_buy_amount = db.Column(db.Float, comment='龙虎榜买入额')
    lhb_sell_amount = db.Column(db.Float, comment='龙虎榜卖出额')
    lhb_net_amount = db.Column(db.Float, comment='龙虎榜净买额')
    lhb_trade_amount = db.Column(db.Float, comment='龙虎榜成交额')
    market_total_amount = db.Column(db.Float, comment='市场总成交额')

    # 龙虎榜占比数据
    lhb_net_ratio = db.Column(db.Float, comment='龙虎榜净买额占总成交比(%)')
    lhb_trade_ratio = db.Column(db.Float, comment='龙虎榜成交额占总成交比(%)')

    # 上榜情况
    analysis = db.Column(db.Text, comment='解读')
    reasons = db.Column(db.Text, comment='上榜原因')

    __table_args__ = (
        db.Index('idx_code', 'code'),
        db.UniqueConstraint('code', 'listed_date', 'reasons', 'analysis', 
                        name='uq_lhb_composite'),  # 复合唯一约束
        )

    def __repr__(self):
        return f'<DailyLHB {self.code} - {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'listed_date': self.listed_date,
            'close_price': self.close_price,
            'change_percent': self.change_percent,
            'turnover_rate': self.turnover_rate,
            'circulating_market_cap': self.circulating_market_cap,
            'lhb_buy_amount': self.lhb_buy_amount,
            'lhb_sell_amount': self.lhb_sell_amount,
            'lhb_net_amount': self.lhb_net_amount,
            'lhb_trade_amount': self.lhb_trade_amount,
            'market_total_amount': self.market_total_amount,
            'lhb_net_ratio': self.lhb_net_ratio,
            'lhb_trade_ratio': self.lhb_trade_ratio,
            'analysis': self.analysis,
            'reasons': self.reasons,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_dict(data):
        return DailyLHB(
            code=data.get('code'),
            name=data.get('name'),
            listed_date=data.get('listed_date'),
            close_price=data.get('close_price'),
            change_percent=data.get('change_percent'),
            turnover_rate=data.get('turnover_rate'),
            circulating_market_cap=data.get('circulating_market_cap'),
            lhb_buy_amount=data.get('lhb_buy_amount'),
            lhb_sell_amount=data.get('lhb_sell_amount'),
            lhb_net_amount=data.get('lhb_net_amount'),
            lhb_trade_amount=data.get('lhb_trade_amount'),
            market_total_amount=data.get('market_total_amount'),
            lhb_net_ratio=data.get('lhb_net_ratio'),
            lhb_trade_ratio=data.get('lhb_trade_ratio'),
            analysis=data.get('analysis'),
            reasons=data.get('reasons'),
        )
