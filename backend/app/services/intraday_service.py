"""
分时数据服务
负责获取和存储股票分时交易数据
"""

from datetime import datetime
from app.services.base_service import BaseService
from app.models.stock.stock_info import StockInfo
from app.models.stock.intraday_data import IntraDayData
from app.models import db
from app.utils.time_helper import get_current_time


class IntraDayDataService(BaseService):
    """
    分时数据服务类
    
    负责追踪股票的分时数据采集和存储
    """
    
    def __init__(self):
        super().__init__()
    
    def fetch_and_save_intraday_data(self):
        """
        获取并保存追踪股票的分时数据
        
        Returns:
            dict: 包含成功和失败信息的字典
        """
        self.logger.info("开始获取追踪股票的分时数据")
        
        # 1. 查询所有 tracking=True 的股票
        tracked_stocks = StockInfo.query.filter_by(tracking=True).all()
        
        if not tracked_stocks:
            self.logger.info("没有需要追踪的股票")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        self.logger.info(f"找到 {len(tracked_stocks)} 只需要追踪的股票")
        
        success_count = 0
        failed_count = 0
        
        # 2. 遍历每只股票，获取分时数据
        for stock in tracked_stocks:
            try:
                count = self._fetch_stock_intraday_data(stock.code)
                if count > 0:
                    success_count += 1
                    self.logger.info(f"股票 {stock.code} {stock.name} 分时数据获取成功，共 {count} 条")
                else:
                    failed_count += 1
                    self.logger.warning(f"股票 {stock.code} {stock.name} 未获取到分时数据")
            except Exception as e:
                failed_count += 1
                self.logger.error(f"股票 {stock.code} {stock.name} 分时数据获取失败: {str(e)}")
        
        result = {
            'success': success_count,
            'failed': failed_count,
            'total': len(tracked_stocks)
        }
        
        self.logger.info(f"分时数据获取完成，成功: {success_count}，失败: {failed_count}，总计: {len(tracked_stocks)}")
        return result
    
    def _fetch_stock_intraday_data(self, stock_code: str) -> int:
        """
        获取单只股票的分时数据
        
        Args:
            stock_code: 股票代码
            
        Returns:
            int: 保存的数据条数
        """
        try:
            # 获取当前日期
            current_date = get_current_time(fmt='%Y%m%d')
            
            # 从 AkShare 获取分时数据
            # stock_zh_a_hist_min_em 接口参数:
            # symbol: 股票代码
            # period: 1(1分钟), 5(5分钟), 15(15分钟), 30(30分钟), 60(60分钟)
            # adjust: 不复权, qfq(前复权), hfq(后复权)
            intraday_data = self._fetch_from_akshare(
                'stock_zh_a_hist_min_em',
                api_params={
                    'symbol': stock_code,
                    'period': '1',  # 1分钟数据
                    'adjust': '',  # 不复权
                    'start_date': f'{current_date} 09:30:00',
                    'end_date': f'{current_date} 15:00:00'
                }
            )
            
            if not intraday_data:
                return 0
            
            # 转换数据格式
            mapped_data = []
            for item in intraday_data:
                try:
                    # AkShare 返回的字段: 时间, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 最新价
                    trade_time_str = item.get('时间', '')
                    if not trade_time_str:
                        continue
                    
                    # 解析交易时间
                    trade_time = datetime.strptime(trade_time_str, '%Y-%m-%d %H:%M:%S')
                    
                    mapped_item = {
                        'stock_code': stock_code,
                        'date': trade_time.date(),
                        'trade_time': trade_time,
                        'price': float(item.get('收盘', 0)),  # 使用收盘价作为成交价
                        'volume': int(item.get('成交量', 0)) if item.get('成交量') else None,
                        'trade_type': None  # AkShare 接口不提供成交类型
                    }
                    mapped_data.append(mapped_item)
                    
                except Exception as e:
                    self.logger.warning(f"解析分时数据失败: {str(e)}, 数据: {item}")
                    continue
            
            if not mapped_data:
                return 0
            
            # 保存到数据库
            saved_count = self._save_intraday_to_db(mapped_data)
            return saved_count
            
        except Exception as e:
            self.logger.error(f"获取股票 {stock_code} 分时数据失败: {str(e)}")
            raise
    
    def _save_intraday_to_db(self, data_list: list) -> int:
        """
        保存分时数据到数据库
        
        由于 IntraDayData 有 unique constraint (stock_code, trade_time),
        需要特殊处理重复数据
        
        Args:
            data_list: 分时数据列表
            
        Returns:
            int: 成功保存的数据条数
        """
        saved_count = 0
        
        for data in data_list:
            try:
                stock_code = data.get('stock_code')
                trade_time = data.get('trade_time')
                
                if not stock_code or not trade_time:
                    continue
                
                # 检查是否已存在
                existing = IntraDayData.query.filter_by(
                    stock_code=stock_code,
                    trade_time=trade_time
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.price = data.get('price')
                    existing.volume = data.get('volume')
                    existing.trade_type = data.get('trade_type')
                    existing.updated_at = datetime.now()
                else:
                    # 创建新记录
                    new_record = IntraDayData(
                        stock_code=stock_code,
                        date=data.get('date'),
                        trade_time=trade_time,
                        price=data.get('price'),
                        volume=data.get('volume'),
                        trade_type=data.get('trade_type')
                    )
                    db.session.add(new_record)
                
                saved_count += 1
                
            except Exception as e:
                self.logger.error(f"保存分时数据失败: {str(e)}, 数据: {data}")
                continue
        
        # 提交事务
        try:
            db.session.commit()
            self.logger.info(f"成功保存 {saved_count} 条分时数据")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"分时数据提交失败: {str(e)}")
            raise
        
        return saved_count
