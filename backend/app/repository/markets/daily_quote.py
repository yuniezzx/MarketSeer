"""
每日行情数据 Repository
"""

from typing import List, Dict, Any, Optional
from app.models.markets.daily_quote import DailyMarketQuote
from app.repository.base import BaseRepository
from app.models.base import db


class DailyMarketQuoteRepository(BaseRepository[DailyMarketQuote]):
    """每日行情数据 Repository"""

    def __init__(self):
        super().__init__(DailyMarketQuote)

    def bulk_upsert(self, items: List[Dict[str, Any]]) -> tuple[int, int]:
        """
        批量插入或更新每日行情数据

        Args:
            items: 行情数据列表

        Returns:
            (创建数量, 更新数量)
        """
        created_count = 0
        updated_count = 0

        for item in items:
            code = item.get("code")
            trade_date = item.get("trade_date")

            if not code or not trade_date:
                continue

            # 使用复合键查找现有记录
            existing = self.get_by_filters(
                {"code": code, "trade_date": trade_date}, limit=1
            )

            if existing:
                # 更新现有记录
                self.update(existing[0].id, item)
                updated_count += 1
            else:
                # 创建新记录
                self.create(item)
                created_count += 1

        db.session.commit()
        return (created_count, updated_count)

    def get_by_date_range(
        self, start_date: str, end_date: str, limit: Optional[int] = None
    ) -> List[DailyMarketQuote]:
        """
        获取日期范围内的行情数据

        Args:
            start_date: 起始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            limit: 返回数量限制

        Returns:
            行情数据列表
        """
        query = self.model.query.filter(
            self.model.trade_date >= start_date, self.model.trade_date <= end_date
        ).order_by(self.model.trade_date.desc(), self.model.code.asc())

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_by_code(
        self, code: str, limit: Optional[int] = None
    ) -> List[DailyMarketQuote]:
        """
        获取指定股票代码的行情数据

        Args:
            code: 股票代码
            limit: 返回数量限制

        Returns:
            行情数据列表
        """
        query = self.model.query.filter(self.model.code == code).order_by(
            self.model.trade_date.desc()
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_by_trade_date(self, trade_date: str) -> List[DailyMarketQuote]:
        """
        获取指定交易日的所有行情数据

        Args:
            trade_date: 交易日期 (YYYYMMDD)

        Returns:
            行情数据列表
        """
        return (
            self.model.query.filter(self.model.trade_date == trade_date)
            .order_by(self.model.code.asc())
            .all()
        )
