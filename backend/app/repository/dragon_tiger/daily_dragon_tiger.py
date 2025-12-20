"""
龙虎榜数据 Repository

提供龙虎榜数据的数据库操作接口
"""

from typing import List, Dict, Any, Optional
from app.repository.base import BaseRepository
from app.models.dragon_tiger.daily_dragon_tiger import DailyDragonTiger
from logger import logger


class DailyDragonTigerRepository(BaseRepository[DailyDragonTiger]):
    """
    龙虎榜数据 Repository

    提供龙虎榜数据的增删改查操作
    大部分方法继承自 BaseRepository，只添加特殊的业务逻辑
    """

    def __init__(self):
        super().__init__(DailyDragonTiger)

    def bulk_upsert(self, items: List[Dict[str, Any]]) -> tuple[int, int]:
        """
        批量插入或更新龙虎榜记录

        根据 (code, listed_date, reasons, analysis) 复合键判断是否存在：
        - 存在则更新
        - 不存在则创建

        使用四字段复合键确保同一股票同一天的不同上榜原因/解读被视为不同记录

        Args:
            items: 龙虎榜数据字典列表，每个字典必须包含 code 和 listed_date

        Returns:
            (创建数量, 更新数量)
        """
        created_count = 0
        updated_count = 0

        try:
            for item in items:
                code = item.get("code")
                listed_date = item.get("listed_date")
                reasons = item.get("reasons", "")
                analysis = item.get("analysis", "")

                if not code or not listed_date:
                    logger.warning(f"跳过无效记录: code={code}, listed_date={listed_date}")
                    continue

                # 使用四字段复合键查找现有记录
                # 将 None 转换为空字符串以保持一致性
                reasons = reasons if reasons else ""
                analysis = analysis if analysis else ""

                existing = self.get_by_filters(
                    {
                        "code": code,
                        "listed_date": listed_date,
                        "reasons": reasons,
                        "analysis": analysis,
                    },
                    limit=1,
                )

                if existing:
                    # 更新现有记录
                    record = existing[0]
                    for key, value in item.items():
                        if hasattr(record, key) and key not in ["code", "listed_date"]:
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
            logger.info(f"龙虎榜数据批量操作完成: 创建 {created_count} 条, 更新 {updated_count} 条")
            return (created_count, updated_count)

        except Exception as e:
            logger.error(f"批量 upsert 失败: {e}")
            from app.models.base import db

            db.session.rollback()
            return (0, 0)

    def get_by_date_range(self, start_date: str, end_date: str) -> List[DailyDragonTiger]:
        """
        获取指定日期范围内的龙虎榜数据

        Args:
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)

        Returns:
            龙虎榜数据列表
        """
        try:
            from app.models.base import db

            query = db.session.query(self.model)

            # 日期范围过滤
            query = query.filter(
                self.model.listed_date >= start_date, self.model.listed_date <= end_date
            )

            records = query.all()
            logger.info(f"查询日期范围 {start_date} 到 {end_date}，返回 {len(records)} 条记录")
            return records

        except Exception as e:
            logger.error(f"日期范围查询失败: {e}")
            logger.exception("详细错误信息:")
            return []
