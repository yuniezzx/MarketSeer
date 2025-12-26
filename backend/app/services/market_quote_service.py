"""
每日行情数据服务

提供每日行情数据的业务逻辑处理
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from .base_service import BaseService
from app.repository import DailyMarketQuoteRepository
from app.mapping.markets.daily_quote_config import API_PRIORITY_CONFIG
from app.data_sources import ClientManager


class MarketQuoteService(BaseService):
    """
    每日行情数据服务

    提供每日行情数据的获取、存储、查询等业务功能
    """

    def __init__(self):
        super().__init__()
        self.repository = DailyMarketQuoteRepository()
        self.client_manager = ClientManager()

    def import_by_date(self, trade_date: str) -> tuple[bool, str, int, int]:
        """
        导入指定日期的行情数据到数据库

        Args:
            trade_date: 交易日期 (格式: YYYYMMDD，如 '20251220')

        Returns:
            (成功标志, 消息, 创建数量, 更新数量)
        """
        try:
            self.logger.info(f"开始导入行情数据: {trade_date}")

            # 1. 按优先级尝试获取数据
            data = []
            for api_config in API_PRIORITY_CONFIG:
                api_name = api_config["name"]
                fetch_func = api_config["fetch_func"]
                
                try:
                    self.logger.info(f"尝试从 {api_name} 获取数据")
                    data = fetch_func(trade_date, self.client_manager)
                    
                    if data:
                        self.logger.info(f"成功从 {api_name} 获取 {len(data)} 条数据")
                        break
                    else:
                        self.logger.warning(f"{api_name} 未返回数据")
                except Exception as e:
                    self.logger.error(f"{api_name} 获取数据失败: {str(e)}")
                    continue

            if not data:
                msg = f"未获取到行情数据: {trade_date}"
                self.logger.warning(msg)
                return (False, msg, 0, 0)

            # 2. 批量插入/更新数据库
            created, updated = self.repository.bulk_upsert(data)

            msg = f"行情数据导入完成: {trade_date} - 创建 {created} 条, 更新 {updated} 条"
            self.logger.info(msg)
            return (True, msg, created, updated)

        except Exception as e:
            msg = f"导入行情数据失败: {trade_date} - {str(e)}"
            self.logger.error(msg)
            self.logger.exception("详细错误信息:")
            return (False, msg, 0, 0)

    def daily_update(self, trade_date: Optional[str] = None) -> bool:
        """
        每日行情数据更新

        Args:
            trade_date: 可选的日期 (格式: YYYYMMDD)，不提供则使用当前日期

        Returns:
            是否成功
        """
        if not trade_date:
            # 使用当前日期
            trade_date = datetime.now().strftime("%Y%m%d")

        success, msg, created, updated = self.import_by_date(trade_date)

        if success:
            self.logger.info(f"每日更新成功: {msg}")
        else:
            self.logger.error(f"每日更新失败: {msg}")

        return success

    def get_by_trade_date(self, trade_date: str) -> List[Dict[str, Any]]:
        """
        获取指定交易日的所有行情数据

        Args:
            trade_date: 交易日期 (格式: YYYY-MM-DD 或 YYYYMMDD)

        Returns:
            行情数据列表
        """
        try:
            # 转换日期格式为 YYYY-MM-DD
            if len(trade_date) == 8:
                trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"

            self.logger.info(f"查询行情数据: {trade_date}")

            # 从数据库查询
            records = self.repository.get_by_trade_date(trade_date)

            # 转换为字典列表
            result = [record.to_dict() for record in records]

            self.logger.info(f"查询成功，返回 {len(result)} 条记录")
            return result

        except Exception as e:
            self.logger.error(f"查询行情数据失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return []

    def get_by_code(self, code: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取指定股票代码的历史行情数据

        Args:
            code: 股票代码
            limit: 限制返回数量

        Returns:
            行情数据列表
        """
        try:
            self.logger.info(f"查询股票行情: {code}, 限制: {limit}")

            # 从数据库查询
            records = self.repository.get_by_code(code, limit)

            # 转换为字典列表
            result = [record.to_dict() for record in records]

            self.logger.info(f"查询成功，返回 {len(result)} 条记录")
            return result

        except Exception as e:
            self.logger.error(f"查询股票行情失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return []

    def get_by_date_range(
        self, start_date: str, end_date: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取指定日期范围的行情数据

        Args:
            start_date: 开始日期 (格式: YYYY-MM-DD 或 YYYYMMDD)
            end_date: 结束日期 (格式: YYYY-MM-DD 或 YYYYMMDD)
            limit: 限制返回数量

        Returns:
            行情数据列表
        """
        try:
            # 转换日期格式为 YYYY-MM-DD
            if len(start_date) == 8:
                start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            if len(end_date) == 8:
                end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"

            self.logger.info(f"查询行情数据: {start_date} 到 {end_date}, 限制: {limit}")

            # 从数据库查询
            records = self.repository.get_by_date_range(start_date, end_date, limit)

            # 转换为字典列表
            result = [record.to_dict() for record in records]

            self.logger.info(f"查询成功，返回 {len(result)} 条记录")
            return result

        except Exception as e:
            self.logger.error(f"查询行情数据失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return []
