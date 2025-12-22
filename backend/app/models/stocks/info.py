from ..base import BaseModel, db


class StockInfo(BaseModel):
    """
    股票基础信息表

    存储股票的基本信息，包括代码、名称、市场、行业等
    """

    __tablename__ = "stock_info"

    # 基本信息
    code = db.Column(db.String(20), unique=True, nullable=False, index=True, comment="股票代码")
    name = db.Column(db.String(100), nullable=False, comment="股票名称")
    full_name = db.Column(db.String(200), comment="股票全称")

    # 市场信息
    market = db.Column(db.String(20), nullable=False, index=True, comment="市场（SH/SZ等）")

    # 行业分类
    industry_code = db.Column(db.String(50), comment="行业代码")
    industry = db.Column(db.String(50), index=True, comment="行业分类")

    # 重要日期
    establish_date = db.Column(db.Date, comment="成立日期")
    list_date = db.Column(db.Date, comment="上市日期")

    # 主营范围
    main_operation_business = db.Column(db.Text, comment="主营业务范围")
    operating_scope = db.Column(db.Text, comment="经营范围")

    # 状态信息
    status = db.Column(db.String(20), default="上市", comment="状态（上市/退市/停牌）")
    tracking = db.Column(db.Boolean, default=False, index=True, comment="是否追踪分时数据")

    # 创建复合索引
    __table_args__ = (
        db.Index("idx_market_code", "market", "code"),
        db.Index("idx_industry", "industry"),
    )

    # 字符串表示
    def __repr__(self):
        return f"<StockInfo {self.code} - {self.name}>"
