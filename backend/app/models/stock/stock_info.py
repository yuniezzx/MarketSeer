"""
股票基础信息模型
"""

from ..base import BaseModel, db


class StockInfo(BaseModel):
    """
    股票基础信息表

    存储股票的基本信息，包括代码、名称、市场、行业等
    """

    __tablename__ = 'stock_info'

    # 基本信息
    code = db.Column(db.String(20), unique=True, nullable=False, index=True, comment='股票代码')
    name = db.Column(db.String(100), nullable=False, comment='股票名称')
    full_name = db.Column(db.String(200), comment='股票全称')

    # 市场信息
    market = db.Column(db.String(20), nullable=False, index=True, comment='市场（SH/SZ等）')

    # 行业分类
    industry_code = db.Column(db.String(50), comment='行业代码')
    industry = db.Column(db.String(50), index=True, comment='行业分类')

    # 重要日期
    establish_date = db.Column(db.String(20), comment='成立日期')
    list_date = db.Column(db.String(20), comment='上市日期')

    # 主营范围
    main_operation_business = db.Column(db.Text, comment='主营业务范围')
    operating_scope = db.Column(db.Text, comment='经营范围')

    # 状态信息
    status = db.Column(db.String(20), default='上市', comment='状态（上市/退市/停牌）')

    # 创建复合索引
    __table_args__ = (
        db.Index('idx_market_code', 'market', 'code'),
        db.Index('idx_industry', 'industry'),
    )

    def __repr__(self):
        return f'<StockInfo {self.code} - {self.name}>'

    def to_dict(self):
        """
        转换为字典格式
        覆盖父类方法以自定义输出字段
        """
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'full_name': self.full_name,
            'market': self.market,
            'industry_code': self.industry_code,
            'industry': self.industry,
            'establish_date': self.establish_date,
            'list_date': self.list_date,
            'main_operation_business': self.main_operation_business,
            'operating_scope': self.operating_scope,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_code(cls, code):
        """根据股票代码查询"""
        return cls.query.filter_by(code=code).first()

    @classmethod
    def get_by_market(cls, market):
        """根据市场查询所有股票"""
        return cls.query.filter_by(market=market).all()

    @classmethod
    def get_by_industry(cls, industry):
        """根据行业查询所有股票"""
        return cls.query.filter_by(industry=industry).all()

    @classmethod
    def search_by_name(cls, keyword):
        """根据名称模糊搜索"""
        return cls.query.filter(cls.name.like(f'%{keyword}%')).all()

    @classmethod
    def search_by_code(cls, keyword):
        """根据代码模糊搜索"""
        return cls.query.filter(cls.code.like(f'%{keyword}%')).all()

    @staticmethod
    def from_dict(data):
        """从字典创建实例"""
        return StockInfo(
            code=data.get('code'),
            name=data.get('name'),
            full_name=data.get('full_name'),
            market=data.get('market'),
            industry_code=data.get('industry_code'),
            industry=data.get('industry'),
            establish_date=data.get('establish_date'),
            list_date=data.get('list_date'),
            main_operation_business=data.get('main_operation_business'),
            operating_scope=data.get('operating_scope'),
            status=data.get('status', '上市'),
        )
