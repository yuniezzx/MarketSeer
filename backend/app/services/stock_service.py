"""
股票数据服务
负责从多数据源采集、整合股票数据
"""

from app.models import StockInfo, db
from app.mapping import stock_info_mapper
from app.utils import get_market_from_code, format_stock_code
from .base_service import BaseService


class StockInfoService(BaseService):
    """股票数据服务类，继承 BaseService"""

    def get_stock_by_code(self, code):
        """
        根据股票代码获取股票信息

        Args:
            code: 股票代码

        Returns:
            StockInfo: 股票信息对象
        """
        return StockInfo.query.filter_by(code=code).first()

    def search_stocks(self, keyword):
        """
        搜索股票

        Args:
            keyword: 搜索关键词

        Returns:
            list: 股票列表
        """
        return StockInfo.query.filter(
            db.or_(StockInfo.code.like(f'%{keyword}%'), StockInfo.name.like(f'%{keyword}%'))
        ).all()

    def add_stock_by_code(self, code):
        """
        添加新股票通过代码

        Args:
            code: 股票代码

        Returns:
            StockInfo: 新增的股票信息对象
        """
        # 先检查是否已存在
        existing_stock = self.get_stock_by_code(code)
        if existing_stock:
            return existing_stock

        # 从 AkShare 获取股票信息
        em_info_data = self._fetch_from_akshare('stock_individual_info_em', {'symbol': code})
        xq_info_data = self._fetch_from_akshare(
            'stock_individual_basic_info_xq', {'symbol': format_stock_code(code, with_market=True)}
        )
        if not em_info_data:
            self.logger.warning(f"无法通过 AkShare 获取东财股票代码 {code} 的信息")
            return None
        if not xq_info_data:
            self.logger.warning(f"无法通过 AkShare 获取雪球股票代码 {code} 的信息")

        # 使用映射函数处理数据源
        mapping_data = stock_info_mapper(em_source=em_info_data, xq_source=xq_info_data)
        market = get_market_from_code(code)
        mapping_data['market'] = market
        
        self.logger.info(f"添加新股票，代码: {code}, 映射数据: {mapping_data}")
        
        # 保存到数据库
        self._save_to_db(StockInfo, [mapping_data], unique_fields=['code'])
        return self.get_stock_by_code(code)

    def update_stock_tracking(self, code, tracking):
        """
        更新股票的追踪状态
        
        Args:
            code: 股票代码
            tracking: 是否追踪 (bool)
        
        Returns:
            StockInfo: 更新后的股票对象,如果不存在返回 None
        """
        stock = self.get_stock_by_code(code)
        if not stock:
            return None
        
        stock.tracking = tracking
        db.session.commit()
        
        self.logger.info(f"更新股票 {code} 的追踪状态为: {tracking}")
        return stock
