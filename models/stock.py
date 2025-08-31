"""
股票相关数据模型

包含股票基本信息、价格数据等模型定义
"""

from sqlalchemy import Column, String, Integer, Decimal, Date, DateTime, Boolean, BigInteger, Text, Index
from .base import BaseModel


class StockInfo(BaseModel):
    """股票基本信息模型"""

    __tablename__ = 'stock_info'

    # 核心标识字段
    symbol = Column(String(20), primary_key=True, comment="股票代码（如：000001.SZ）")
    code = Column(String(10), nullable=False, comment="纯数字代码（如：000001）")
    market = Column(String(10), nullable=False, comment="市场类型（SZ/SH/BJ）")

    # 基本信息字段
    name = Column(String(100), nullable=False, comment="股票名称")
    full_name = Column(String(200), comment="公司全称")
    english_name = Column(String(200), comment="英文名称")
    industry = Column(String(100), comment="所属行业")
    sector = Column(String(100), comment="所属板块")
    concept = Column(Text, comment="概念板块（逗号分隔）")

    # 公司基本信息
    company_type = Column(String(50), comment="公司类型")
    legal_representative = Column(String(100), comment="法定代表人")
    registered_capital = Column(Decimal(20, 2), comment="注册资本（万元）")
    establishment_date = Column(Date, comment="成立日期")
    listing_date = Column(Date, comment="上市日期")
    province = Column(String(50), comment="所在省份")
    city = Column(String(50), comment="所在城市")
    address = Column(Text, comment="公司地址")
    website = Column(String(200), comment="公司网站")
    business_scope = Column(Text, comment="经营范围")
    main_business = Column(Text, comment="主营业务")

    # 财务相关字段
    total_shares = Column(BigInteger, comment="总股本（股）")
    circulating_shares = Column(BigInteger, comment="流通股本（股）")
    market_cap = Column(Decimal(20, 2), comment="总市值（元）")
    circulating_market_cap = Column(Decimal(20, 2), comment="流通市值（元）")
    pe_ratio = Column(Decimal(10, 2), comment="市盈率")
    pb_ratio = Column(Decimal(10, 2), comment="市净率")
    eps = Column(Decimal(10, 4), comment="每股收益")
    bps = Column(Decimal(10, 4), comment="每股净资产")
    roe = Column(Decimal(8, 4), comment="净资产收益率")
    debt_ratio = Column(Decimal(8, 4), comment="资产负债率")

    # 交易相关字段
    status = Column(String(20), default="正常", comment="交易状态")
    is_st = Column(Boolean, default=False, comment="是否ST股票")
    currency = Column(String(10), default="CNY", comment="交易货币")
    lot_size = Column(Integer, default=100, comment="每手股数")

    # 描述字段
    description = Column(Text, comment="公司简介")
    remarks = Column(Text, comment="备注信息")
    last_sync_time = Column(DateTime, comment="最后同步时间")

    # 索引定义
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_name', 'name'),
        Index('idx_industry', 'industry'),
        Index('idx_market', 'market'),
        Index('idx_listing_date', 'listing_date'),
        Index('idx_market_industry', 'market', 'industry'),
        Index('idx_status_active', 'status', 'is_active'),
    )

    def __repr__(self):
        return f"<StockInfo(symbol='{self.symbol}', name='{self.name}', market='{self.market}')>"


class StockPrice(BaseModel):
    """股票价格数据模型"""

    __tablename__ = 'stock_price'

    # 主键：股票代码 + 日期
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    symbol = Column(String(20), nullable=False, comment="股票代码")
    trade_date = Column(Date, nullable=False, comment="交易日期")

    # 价格数据
    open_price = Column(Decimal(10, 3), comment="开盘价")
    high_price = Column(Decimal(10, 3), comment="最高价")
    low_price = Column(Decimal(10, 3), comment="最低价")
    close_price = Column(Decimal(10, 3), comment="收盘价")
    pre_close = Column(Decimal(10, 3), comment="昨收价")

    # 交易量数据
    volume = Column(BigInteger, comment="成交量（股）")
    amount = Column(Decimal(20, 2), comment="成交额（元）")

    # 涨跌数据
    change = Column(Decimal(10, 3), comment="涨跌额")
    pct_change = Column(Decimal(8, 4), comment="涨跌幅（%）")

    # 其他指标
    turnover_rate = Column(Decimal(8, 4), comment="换手率（%）")

    # 索引定义
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'trade_date'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_symbol', 'symbol'),
    )

    def __repr__(self):
        return f"<StockPrice(symbol='{self.symbol}', date='{self.trade_date}', close={self.close_price})>"


class Stock(BaseModel):
    """股票汇总模型（可选）"""

    __tablename__ = 'stock'

    symbol = Column(String(20), primary_key=True, comment="股票代码")
    name = Column(String(100), nullable=False, comment="股票名称")
    market = Column(String(10), nullable=False, comment="市场类型")
    industry = Column(String(100), comment="所属行业")

    # 最新价格信息
    latest_price = Column(Decimal(10, 3), comment="最新价格")
    latest_change = Column(Decimal(8, 4), comment="最新涨跌幅")
    latest_update = Column(DateTime, comment="最新更新时间")

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}', price={self.latest_price})>"
