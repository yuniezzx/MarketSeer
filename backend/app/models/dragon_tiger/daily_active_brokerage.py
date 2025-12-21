from ..base import BaseModel, db


class DailyActiveBrokerage(BaseModel):
    """
    每日活跃券商数据表

    存储每日活跃券商的交易信息，包括券商名称、
    买入额、卖出额及净买额等
    """

    __tablename__ = "daily_active_brokerage"

    # 基本信息
    brokerage_code = db.Column(db.String(20), nullable=False, index=True, comment="营业部代码")
    brokerage_name = db.Column(db.String(100), nullable=False, comment="营业部名称")
    listed_date = db.Column(db.String(20), comment="上榜日")

    # 股票数据
    buy_stock_count = db.Column(db.Integer, comment="买入个股数")
    sell_stock_count = db.Column(db.Integer, comment="卖出个股数")
    buy_total_amount = db.Column(db.Float, comment="买入总金额")
    sell_total_amount = db.Column(db.Float, comment="卖出总金额")
    net_total_amount = db.Column(db.Float, comment="总买卖净额")

    # 买入股票
    buy_stocks = db.Column(db.Text, comment="买入股票")

    # 创建复合索引
    __table_args__ = (
        db.Index("idx_brokerage_code_name", "brokerage_code", "brokerage_name"),
        db.Index("idx_listed_date_brokerage", "listed_date"),
    )

    # 字符串表示
    def __repr__(self):
        return f"<DailyActiveBrokerage {self.brokerage_code} - {self.brokerage_name} - {self.listed_date}>"
