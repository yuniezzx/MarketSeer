"""
每日活跃营业部数据 Repository

提供每日活跃营业部数据的数据库操作接口
"""

from typing import List, Dict, Any
from app.repository.base import BaseRepository
from app.models.dragon_tiger.daily_active_brokerage import DailyActiveBrokerage
from logger import logger

class DailyActiveBrokerageRepository(BaseRepository[DailyActiveBrokerage]):
    """
    每日活跃营业部数据 Repository

    提供每日活跃营业部数据的增删改查操作
    """

    def __init__(self):
        super().__init__(DailyActiveBrokerage)

    def bulk_upsert(self, items: List[Dict[str, Any]]) -> tuple[int, int]:
        """
        批量插入或更新每日活跃营业部记录

        根据 (brokerage_code, listed_date) 复合键判断是否存在:
        - 存在则更新
        - 不存在则创建

        Args:
            items: 营业部数据字典列表

        Returns:
            (创建数量, 更新数量)
        """
        created_count = 0
        updated_count = 0

        try:
            for item in items:
                brokerage_code = item.get("brokerage_code")
                listed_date = item.get("listed_date")

                if not brokerage_code or not listed_date:
                    logger.warning(f"跳过无效记录: brokerage_code={brokerage_code}, listed_date={listed_date}")
                    continue

                # 使用双字段复合键查找现有记录
                existing = self.get_by_filters(
                    {
                        "brokerage_code": brokerage_code,
                        "listed_date": listed_date,
                    },
                    limit=1,
                )

                if existing:
                    # 更新现有记录
                    record = existing[0]
                    for key, value in item.items():
                        if hasattr(record, key) and key not in ["brokerage_code", "listed_date"]:
                            setattr(record, key, value)
                    updated_count += 1
                else:
                    # 创建新记录
                    record = self.model(**item)
                    from app.models.base import db
                    db.session.add(record)
                    created_count += 1

            # 提交事务
            from app.models.base import db
            db.session.commit()
            logger.info(f"每日活跃营业部数据批量操作完成: 创建 {created_count} 条, 更新 {updated_count} 条")
            return (created_count, updated_count)

        except Exception as e:
            logger.error(f"批量 upsert 失败: {e}")
            from app.models.base import db
            db.session.rollback()
            return (0, 0)

    def get_by_date_range(self, start_date: str, end_date: str) -> List[DailyActiveBrokerage]:
        """
        获取指定日期范围内的营业部数据

        Args:
            start_date: 开始日期 (格式: YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYY-MM-DD)

        Returns:
            营业部数据列表
        """
        try:
            from app.models.base import db
            query = db.session.query(self.model)
            query = query.filter(
                self.model.listed_date >= start_date,
                self.model.listed_date <= end_date
            )
            records = query.all()
            logger.info(f"查询日期范围 {start_date} 到 {end_date},返回 {len(records)} 条记录")
            return records
        except Exception as e:
            logger.error(f"日期范围查询失败: {e}")
            logger.exception("详细错误信息:")
            return []
