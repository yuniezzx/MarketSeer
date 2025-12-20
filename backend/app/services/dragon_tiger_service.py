"""
龙虎榜数据服务

提供龙虎榜数据的业务逻辑处理
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
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

    def get_daily_dragon_tiger(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        获取最近N天的龙虎榜数据

        Args:
            days_back: 查询最近几天的数据 (默认7天)

        Returns:
            龙虎榜数据列表
        """
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back - 1)

            # 格式化日期为 YYYY-MM-DD
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            self.logger.info(f"查询龙虎榜数据: {start_date_str} 到 {end_date_str}")

            # 从数据库查询
            records = self.repository.get_by_date_range(
                start_date=start_date_str, end_date=end_date_str
            )

            # 转换为字典列表
            result = [record.to_dict() for record in records]

            self.logger.info(f"查询成功，返回 {len(result)} 条记录")
            return result

        except Exception as e:
            self.logger.error(f"查询龙虎榜数据失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return []

    def get_dragon_tiger_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取指定日期范围的龙虎榜数据

        Args:
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)

        Returns:
            龙虎榜数据列表
        """
        try:
            # 转换日期格式 YYYY-MM-DD
            start_date_formatted = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            end_date_formatted = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"

            self.logger.info(f"查询龙虎榜数据: {start_date_formatted} 到 {end_date_formatted}")

            # 从数据库查询
            records = self.repository.get_by_date_range(
                start_date=start_date_formatted,
                end_date=end_date_formatted,
            )

            # 转换为字典列表
            result = [record.to_dict() for record in records]

            self.logger.info(f"查询成功，返回 {len(result)} 条记录")
            return result

        except Exception as e:
            self.logger.error(f"查询龙虎榜数据失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return []
