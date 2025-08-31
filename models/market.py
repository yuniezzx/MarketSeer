"""
市场数据模型

包含市场指数、板块等相关模型定义
"""

from sqlalchemy import Column, String, Integer, Decimal, Date, DateTime, Boolean, Text, Index
from .base import BaseModel


class Market(BaseModel):
    """市场基本信息模型"""

    __tablename__ = 'market'

    code = Column(String(20), primary_key=True, comment="市场代码（如：SZ, SH, BJ）")
    name = Column(String(100), nullable=False, comment="市场名称")
    full_name = Column(String(200), comment="市场全称")
    country = Column(String(50), default="CN", comment="国家代码")
    currency = Column(String(10), default="CNY", comment="交易货币")
    timezone = Column(String(50), default="Asia/Shanghai", comment="时区")

    # 交易时间
    trading_start = Column(String(10), comment="交易开始时间（如：09:30）")
    trading_end = Column(String(10), comment="交易结束时间（如：15:00）")
    lunch_break_start = Column(String(10), comment="午休开始时间")
    lunch_break_end = Column(String(10), comment="午休结束时间")

    # 其他信息
    description = Column(Text, comment="市场描述")
    website = Column(String(200), comment="官方网站")

    def __repr__(self):
        return f"<Market(code='{self.code}', name='{self.name}')>"


class Index(BaseModel):
    """指数信息模型"""

    __tablename__ = 'index_info'

    # 基本信息
    code = Column(String(20), primary_key=True, comment="指数代码（如：000001.SH）")
    name = Column(String(100), nullable=False, comment="指数名称")
    full_name = Column(String(200), comment="指数全称")
    market = Column(String(10), nullable=False, comment="所属市场")
    category = Column(String(50), comment="指数类别（综合/行业/主题等）")

    # 指数属性
    base_date = Column(Date, comment="基准日期")
    base_point = Column(Decimal(10, 2), comment="基准点数")
    weight_method = Column(String(50), comment="加权方式（市值加权/等权重等）")
    constituent_count = Column(Integer, comment="成分股数量")

    # 发布信息
    publisher = Column(String(100), comment="发布机构")
    publish_date = Column(Date, comment="发布日期")
    calculation_method = Column(Text, comment="计算方法描述")

    # 状态信息
    status = Column(String(20), default="正常", comment="指数状态")

    # 索引定义
    __table_args__ = (
        Index('idx_market', 'market'),
        Index('idx_category', 'category'),
        Index('idx_name', 'name'),
    )

    def __repr__(self):
        return f"<Index(code='{self.code}', name='{self.name}', market='{self.market}')>"


class IndexPrice(BaseModel):
    """指数价格数据模型"""

    __tablename__ = 'index_price'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    code = Column(String(20), nullable=False, comment="指数代码")
    trade_date = Column(Date, nullable=False, comment="交易日期")

    # 价格数据
    open_point = Column(Decimal(10, 2), comment="开盘点数")
    high_point = Column(Decimal(10, 2), comment="最高点数")
    low_point = Column(Decimal(10, 2), comment="最低点数")
    close_point = Column(Decimal(10, 2), comment="收盘点数")
    pre_close = Column(Decimal(10, 2), comment="昨收点数")

    # 交易数据
    volume = Column(Decimal(20, 2), comment="成交量")
    amount = Column(Decimal(20, 2), comment="成交额")

    # 涨跌数据
    change = Column(Decimal(10, 2), comment="涨跌点数")
    pct_change = Column(Decimal(8, 4), comment="涨跌幅（%）")

    # 索引定义
    __table_args__ = (
        Index('idx_code_date', 'code', 'trade_date'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_code', 'code'),
    )

    def __repr__(self):
        return f"<IndexPrice(code='{self.code}', date='{self.trade_date}', close={self.close_point})>"


class Sector(BaseModel):
    """板块信息模型"""

    __tablename__ = 'sector'

    # 基本信息
    code = Column(String(20), primary_key=True, comment="板块代码")
    name = Column(String(100), nullable=False, comment="板块名称")
    category = Column(String(50), comment="板块类别（行业/概念/地域等）")
    parent_code = Column(String(20), comment="父级板块代码")
    level = Column(Integer, default=1, comment="板块层级")

    # 板块属性
    stock_count = Column(Integer, comment="包含股票数量")
    total_market_cap = Column(Decimal(20, 2), comment="总市值")
    avg_pe_ratio = Column(Decimal(10, 2), comment="平均市盈率")

    # 描述信息
    description = Column(Text, comment="板块描述")

    # 状态信息
    status = Column(String(20), default="正常", comment="板块状态")

    # 索引定义
    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_parent_code', 'parent_code'),
        Index('idx_name', 'name'),
    )

    def __repr__(self):
        return f"<Sector(code='{self.code}', name='{self.name}', category='{self.category}')>"


class SectorPrice(BaseModel):
    """板块价格数据模型"""

    __tablename__ = 'sector_price'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    code = Column(String(20), nullable=False, comment="板块代码")
    trade_date = Column(Date, nullable=False, comment="交易日期")

    # 价格数据
    open_price = Column(Decimal(10, 3), comment="开盘价")
    high_price = Column(Decimal(10, 3), comment="最高价")
    low_price = Column(Decimal(10, 3), comment="最低价")
    close_price = Column(Decimal(10, 3), comment="收盘价")
    pre_close = Column(Decimal(10, 3), comment="昨收价")

    # 涨跌数据
    change = Column(Decimal(10, 3), comment="涨跌额")
    pct_change = Column(Decimal(8, 4), comment="涨跌幅（%）")

    # 统计数据
    up_count = Column(Integer, comment="上涨股票数")
    down_count = Column(Integer, comment="下跌股票数")
    unchanged_count = Column(Integer, comment="平盘股票数")

    # 索引定义
    __table_args__ = (
        Index('idx_code_date', 'code', 'trade_date'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_code', 'code'),
    )

    def __repr__(self):
        return f"<SectorPrice(code='{self.code}', date='{self.trade_date}', close={self.close_price})>"
