"""
股票数据服务
负责从多数据源采集、整合股票数据
"""

from datetime import datetime
from app.models import StockInfo, db
from app.config import Config
from app.mapping import stock_info_mapper
from app.utils.logger import get_logger
from app.utils.stock_helper import get_market_from_code, format_stock_code

logger = get_logger(__name__)


class StockInfoService:
    """股票数据服务类"""

    def __init__(self):
        self.config = Config()

    def _fetch_from_akshare(self, api_name, api_params=None):
        """
        通用 AkShare 数据获取函数
        Args:
            api_name (str): akshare 接口名称，如 'stock_info_a_code_name'
            api_params (dict): 传递给接口的参数字典
        Returns:
            list: 获取到的数据列表
        """
        logger.info(f"从 AkShare 获取数据，接口: {api_name}, 参数: {api_params}")
        try:
            import akshare as ak

            # 获取接口函数
            api_func = getattr(ak, api_name, None)
            if not api_func:
                logger.error(f"AkShare 未找到接口: {api_name}")
                return []
            # 调用接口
            if api_params:
                df = api_func(**api_params)
            else:
                df = api_func()
            # 转换为 dict list
            if hasattr(df, 'to_dict'):
                return df.to_dict(orient='records')
            else:
                logger.error("AkShare 返回结果无法转换为 dict list")
                return []
        except Exception as e:
            logger.error(f"AkShare 数据获取失败: {str(e)}")
            return []

    def _fetch_from_efinance(self):
        """
        从 eFinance 获取股票数据
        TODO: 实现 eFinance 数据采集逻辑
        """
        logger.info("从 eFinance 获取数据")

        # 示例数据结构，实际需要调用 efinance 库
        # import efinance as ef
        # df = ef.stock.get_realtime_quotes()

        # 临时返回空列表，待后续实现
        return []

    def _save_to_db(self, stocks_data):
        """
        保存股票数据到数据库

        Args:
            stocks_data: 股票数据列表

        Returns:
            int: 更新的记录数
        """
        updated_count = 0

        for stock_data in stocks_data:
            try:
                code = stock_data.get('code')
                existing_stock = StockInfo.query.filter_by(code=code).first()

                if existing_stock:
                    # 更新现有记录
                    for key, value in stock_data.items():
                        if hasattr(existing_stock, key):
                            setattr(existing_stock, key, value)
                    existing_stock.update_time = datetime.now().isoformat()
                else:
                    # 创建新记录
                    new_stock = StockInfo.from_dict(stock_data)
                    db.session.add(new_stock)

                updated_count += 1

            except Exception as e:
                logger.error(f"保存股票 {stock_data.get('code')} 失败: {str(e)}")
                continue

        # 提交事务
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"数据库提交失败: {str(e)}")
            raise

        return updated_count

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

    # 添加新股票通过代码
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
            logger.warning(f"无法通过 AkShare 获取东财股票代码 {code} 的信息")
            return None
        if not xq_info_data:
            logger.warning(f"无法通过 AkShare 获取雪球股票代码 {code} 的信息")

        # 保存到数据库
        try:
            # 从列表中提取第一个元素（因为 _fetch_from_akshare 返回的是列表）
            em_info_dict = em_info_data[0] if em_info_data else None
            xq_info_dict = xq_info_data[0] if xq_info_data else None

            # 使用映射函数处理数据源
            mapping_data = stock_info_mapper(em_source=em_info_dict, xq_source=xq_info_dict)

            # 获取市场信息
            market = get_market_from_code(code)
            mapping_data['market'] = market

            # 创建 StockInfo 实例
            new_stock = StockInfo.from_dict(mapping_data)

            # 添加到数据库会话并提交
            db.session.add(new_stock)
            db.session.commit()

            logger.info(f"成功添加股票 {code}")
            return new_stock
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加股票 {code} 失败: {str(e)}")
            return None
