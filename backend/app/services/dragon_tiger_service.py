"""
龙虎榜数据服务

提供龙虎榜数据的业务逻辑处理
"""

from datetime import datetime
from typing import Optional
from .base_service import BaseService
from app.repository import DailyDragonTigerRepository
from app.mapping.dragon_tiger.daily_mapping import map_daily_dragon_tiger_by_date
from app.data_sources import ClientManager


class DragonTigerService(BaseService):
    """
    龙虎榜数据服务

    提供龙虎榜数据的获取、存储、查询等业务功能
    """

    def __init__(self):
        super().__init__()
        self.repository = DailyDragonTigerRepository()
        self.client_manager = ClientManager()

    def import_by_date(self, date: str) -> tuple[bool, str, int, int]:
        """
        导入指定日期的龙虎榜数据到数据库

        Args:
            date: 日期 (格式: YYYYMMDD，如 '20251219')

        Returns:
            (成功标志, 消息, 创建数量, 更新数量)
        """
        try:
            self.logger.info(f"开始导入龙虎榜数据: {date}")

            # 1. 获取数据
            data = map_daily_dragon_tiger_by_date(date, self.client_manager)

            if not data:
                msg = f"未获取到龙虎榜数据: {date}"
                self.logger.warning(msg)
                return (False, msg, 0, 0)

            # 2. 批量插入/更新数据库
            created, updated = self.repository.bulk_upsert(data)

            msg = f"龙虎榜数据导入完成: {date} - 创建 {created} 条, 更新 {updated} 条"
            self.logger.info(msg)
            return (True, msg, created, updated)

        except Exception as e:
            msg = f"导入龙虎榜数据失败: {date} - {str(e)}"
            self.logger.error(msg)
            self.logger.exception("详细错误信息:")
            return (False, msg, 0, 0)

    def daily_update(self, date: Optional[str] = None):
        """
        每日龙虎榜数据更新

        Args:
            date: 可选的日期 (格式: YYYYMMDD)，不提供则使用当前日期
        """
        if not date:
            # 使用当前日期
            date = datetime.now().strftime("%Y%m%d")

        success, msg, created, updated = self.import_by_date(date)

        if success:
            self.logger.info(f"每日更新成功: {msg}")
        else:
            self.logger.error(f"每日更新失败: {msg}")

        return success
