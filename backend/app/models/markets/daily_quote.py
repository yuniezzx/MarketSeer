from app.models.base import BaseModel, db


class DailyMarketQuote(BaseModel):
    """每日股票行情数据表"""
    __tablename__ = "daily_market_quote"
    
    # 基本信息
    code = db.Column(db.String(20), nullable=False, index=True, comment="股票代码")
    name = db.Column(db.String(100), nullable=False, comment="股票名称")
    trade_date = db.Column(db.String(20), nullable=False, comment="交易日期")
    
    # 价格信息
    open = db.Column(db.Numeric(10, 2), comment="开盘价")
    close = db.Column(db.Numeric(10, 2), comment="收盘价")
    high = db.Column(db.Numeric(10, 2), comment="最高价")
    low = db.Column(db.Numeric(10, 2), comment="最低价")
    pre_close = db.Column(db.Numeric(10, 2), comment="昨收价")
    
    # 成交信息
    volume = db.Column(db.BigInteger, comment="成交量(手)")
    amount = db.Column(db.Numeric(20, 2), comment="成交额(元)")
    
    # 涨跌信息
    change = db.Column(db.Numeric(10, 2), comment="涨跌额")
    change_percent = db.Column(db.Numeric(10, 2), comment="涨跌幅(%)")
    
    # 技术指标
    amplitude = db.Column(db.Numeric(10, 2), comment="振幅(%)")
    turnover_rate = db.Column(db.Numeric(10, 2), comment="换手率(%)")
    volume_ratio = db.Column(db.Numeric(10, 2), comment="量比")
    
    # 估值指标
    pe_ratio_dynamic = db.Column(db.Numeric(10, 2), comment="市盈率(动态)")
    pb_ratio = db.Column(db.Numeric(10, 2), comment="市净率")
    
    # 市值信息
    total_market_cap = db.Column(db.Numeric(20, 2), comment="总市值(亿元)")
    circulating_market_cap = db.Column(db.Numeric(20, 2), comment="流通市值(亿元)")
    
    # 涨速和多周期涨跌
    rise_speed = db.Column(db.Numeric(10, 2), comment="涨速(%)")
    change_5min = db.Column(db.Numeric(10, 2), comment="5分钟涨跌(%)")
    change_60d = db.Column(db.Numeric(10, 2), comment="60日涨跌幅(%)")
    change_ytd = db.Column(db.Numeric(10, 2), comment="年初至今涨跌幅(%)")
    
    # 创建复合索引
    __table_args__ = (
        db.Index("idx_code_trade_date", "code", "trade_date"),
        db.Index("idx_trade_date", "trade_date"),
    )
