from ..base import BaseModel, db


class DailyDragonTiger(BaseModel):
    """
    每日龙虎榜数据表

    存储每日龙虎榜的股票交易信息，包括上榜股票的基本信息、
    交易数据、龙虎榜买卖情况及上榜原因等
    """

    __tablename__ = 'daily_dragon_tiger'

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

    # 创建复合索引
    __table_args__ = (
        db.Index('idx_code_date', 'code', 'listed_date'),
        db.Index('idx_listed_date', 'listed_date'),
    )

    # 字符串表示
    def __repr__(self):
        return f'<DailyDragonTiger {self.code} - {self.name} - {self.listed_date}>'
