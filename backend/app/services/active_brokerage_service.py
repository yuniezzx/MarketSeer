"""
每日活跃营业部数据服务

提供每日活跃营业部数据的业务逻辑处理
"""

from typing import Optional, Dict, Any
from datetime import datetime
from logger import logger
from .base_service import BaseService
from app.repository.dragon_tiger.daily_active_brokerage import DailyActiveBrokerageRepository
from app.data_sources.client_manager import ClientManager
from app.mapping.dragon_tiger.daily_brokerage_mapping import map_daily_active_brokerage_by_date


class ActiveBrokerageService(BaseService):
    """每日活跃营业部数据服务"""
    
    def __init__(self):
        """初始化服务"""
        super().__init__()
        self.repository = DailyActiveBrokerageRepository()
        self.client_manager = ClientManager()
    
    def import_by_date(self, date: str) -> tuple[bool, str, int, int]:
        """
        导入指定日期的每日活跃营业部数据
        
        Args:
            date: 日期字符串,格式: YYYY-MM-DD
            
        Returns:
            tuple: (success, message, created_count, updated_count)
                - success: 是否成功
                - message: 返回消息
                - created_count: 新增记录数
                - updated_count: 更新记录数
        """
        try:
            logger.info(f"开始导入日期 {date} 的每日活跃营业部数据")
            
            # 获取数据
            data = map_daily_active_brokerage_by_date(
                self.client_manager, 
                date
            )
            
            if not data:
                message = f"日期 {date} 没有活跃营业部数据"
                logger.warning(message)
                return False, message, 0, 0
            
            logger.info(f"获取到 {len(data)} 条活跃营业部数据")
            
            # 批量插入或更新
            created_count, updated_count = self.repository.bulk_upsert(data)
            
            message = f"成功导入日期 {date} 的活跃营业部数据: 新增 {created_count} 条,更新 {updated_count} 条"
            logger.info(message)
            
            return True, message, created_count, updated_count
            
        except Exception as e:
            error_msg = f"导入日期 {date} 的活跃营业部数据失败: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg, 0, 0
    
    def daily_update(self, date: Optional[str] = None) -> bool:
        """
        每日更新活跃营业部数据
        
        Args:
            date: 日期字符串,格式: YYYY-MM-DD,默认为当前日期
            
        Returns:
            bool: 是否成功
        """
        try:
            # 如果未指定日期,使用当前日期
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"执行每日活跃营业部数据更新,日期: {date}")
            
            success, message, created, updated = self.import_by_date(date)
            
            if success:
                logger.info(f"每日更新完成: {message}")
            else:
                logger.error(f"每日更新失败: {message}")
            
            return success
            
        except Exception as e:
            logger.exception(f"每日更新活跃营业部数据失败: {str(e)}")
            return False
    
    def get_by_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        获取指定日期范围的活跃营业部数据
        
        Args:
            start_date: 开始日期,格式: YYYY-MM-DD
            end_date: 结束日期,格式: YYYY-MM-DD
            
        Returns:
            Dict: 包含数据和统计信息的字典
        """
        try:
            data = self.repository.get_by_date_range(start_date, end_date)
            
            return {
                "success": True,
                "data": [item.to_dict() for item in data],
                "count": len(data),
                "start_date": start_date,
                "end_date": end_date
            }
            
        except Exception as e:
            logger.exception(f"获取日期范围 {start_date} 至 {end_date} 的活跃营业部数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "count": 0
            }
