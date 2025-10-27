"""
股票数据服务
负责从多数据源采集、整合股票数据
"""
from datetime import datetime
from app.models import StockInfo, db
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StockService:
    """股票数据服务类"""
    
    def __init__(self):
        self.config = Config()
    
    def update_stock_info(self, source='all'):
        """
        更新股票基础信息
        
        Args:
            source: 数据源 ('akshare', 'efinance', 'all')
        
        Returns:
            dict: 更新结果
        """
        try:
            logger.info(f"开始更新股票数据，数据源: {source}")
            
            stocks_data = []
            
            # 根据数据源获取数据
            if source == 'all' or source == 'akshare':
                akshare_data = self._fetch_from_akshare()
                stocks_data.extend(akshare_data)
            
            if source == 'all' or source == 'efinance':
                efinance_data = self._fetch_from_efinance()
                stocks_data.extend(efinance_data)
            
            # 合并和去重
            merged_data = self._merge_data(stocks_data)
            
            # 保存到数据库
            updated_count = self._save_to_db(merged_data)
            
            logger.info(f"股票数据更新完成，共更新 {updated_count} 条记录")
            
            return {
                'updated_rows': updated_count,
                'source': source
            }
            
        except Exception as e:
            logger.error(f"更新股票数据失败: {str(e)}")
            raise
    
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
    
    def _merge_data(self, stocks_data):
        """
        合并多数据源数据，去重并选择优先级高的数据
        
        Args:
            stocks_data: 股票数据列表
        
        Returns:
            list: 合并后的数据
        """
        merged = {}
        
        for stock in stocks_data:
            code = stock.get('code')
            if not code:
                continue
            
            # 如果该股票代码已存在，根据优先级决定是否覆盖
            if code in merged:
                # 这里可以添加数据源优先级逻辑
                # 暂时简单覆盖
                pass
            
            merged[code] = stock
        
        return list(merged.values())
    
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
            db.or_(
                StockInfo.code.like(f'%{keyword}%'),
                StockInfo.name.like(f'%{keyword}%')
            )
        ).all()
