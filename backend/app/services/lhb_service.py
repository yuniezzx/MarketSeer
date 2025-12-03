"""
龙虎榜数据服务
负责从多数据源采集、整合龙虎榜数据
"""

from datetime import datetime
from app.models import DailyLHB, db
from app.mapping import weekly_lhb_mapper
from .base_service import BaseService


class LhbService(BaseService):
    """龙虎榜数据服务类，继承 BaseService"""

    def get_lhb_by_date_range(self, start_date, end_date):
        """
        根据日期范围获取龙虎榜数据

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            list: 龙虎榜数据列表
        """
        return (
            DailyLHB.query.filter(DailyLHB.listed_date >= start_date, DailyLHB.listed_date <= end_date)
            .order_by(DailyLHB.listed_date.desc())
            .all()
        )

    def get_lhb_by_code(self, code, start_date=None, end_date=None):
        """
        根据股票代码获取龙虎榜数据

        Args:
            code: 股票代码
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)

        Returns:
            list: 龙虎榜数据列表
        """
        query = DailyLHB.query.filter_by(code=code)

        if start_date:
            query = query.filter(DailyLHB.listed_date >= start_date)
        if end_date:
            query = query.filter(DailyLHB.listed_date <= end_date)

        return query.order_by(DailyLHB.listed_date.desc()).all()

    def fetch_and_update_lhb_data(self, start_date, end_date):
        """
        从 AkShare 获取并更新龙虎榜数据

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            int: 更新的记录数
        """
        self.logger.info(f"开始获取龙虎榜数据: {start_date} 至 {end_date}")

        # 从 AkShare 获取龙虎榜数据
        lhb_data = self._fetch_from_akshare(
            'stock_lhb_detail_em',
            {'start_date': start_date.replace('-', ''), 'end_date': end_date.replace('-', '')},
        )

        if not lhb_data:
            self.logger.warning(f"无法获取 {start_date} 至 {end_date} 的龙虎榜数据")
            return 0

        # 使用映射函数处理数据
        mapped_data_list = [weekly_lhb_mapper(item) for item in lhb_data]

        # 保存到数据库 (使用 code + listed_date 作为唯一标识)
        updated_count = self._save_lhb_to_db(mapped_data_list)

        self.logger.info(f"龙虎榜数据更新完成，共更新 {updated_count} 条记录")
        return updated_count

    def _save_lhb_to_db(self, data_list):
        """
        保存龙虎榜数据到数据库
        使用 code + listed_date 作为唯一标识

        Args:
            data_list: 要保存的数据列表

        Returns:
            int: 更新的记录数
        """
        updated_count = 0

        for data in data_list:
            try:
                code = data.get('code')
                listed_date = data.get('listed_date')

                if not code or not listed_date:
                    self.logger.warning("数据缺少 code 或 listed_date，跳过")
                    continue

                # 查询是否已存在 (使用 code + listed_date 作为唯一标识)
                existing_record = DailyLHB.query.filter_by(code=code, listed_date=listed_date).first()

                if existing_record:
                    # 更新现有记录
                    for key, value in data.items():
                        if hasattr(existing_record, key):
                            setattr(existing_record, key, value)
                    if hasattr(existing_record, "updated_at"):
                        existing_record.updated_at = datetime.now()
                else:
                    # 创建新记录
                    new_record = DailyLHB.from_dict(data)
                    db.session.add(new_record)

                updated_count += 1

            except Exception as e:
                self.logger.error(f"保存数据 {data.get('code')} - {data.get('listed_date')} 失败: {str(e)}")
                continue

        # 提交事务
        try:
            db.session.commit()
            self.logger.info(f"成功保存 {updated_count} 条龙虎榜记录")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"数据库提交失败: {str(e)}")
            raise

        return updated_count

    def get_latest_lhb_date(self):
        """
        获取数据库中最新的龙虎榜日期

        Returns:
            str: 最新日期 (YYYY-MM-DD) 或 None
        """
        latest_record = DailyLHB.query.order_by(DailyLHB.listed_date.desc()).first()

        return latest_record.listed_date if latest_record else None

    def search_lhb(self, keyword):
        """
        搜索龙虎榜数据

        Args:
            keyword: 搜索关键词 (股票代码或名称)

        Returns:
            list: 龙虎榜数据列表
        """
        return (
            DailyLHB.query.filter(
                db.or_(DailyLHB.code.like(f'%{keyword}%'), DailyLHB.name.like(f'%{keyword}%'))
            )
            .order_by(DailyLHB.listed_date.desc())
            .all()
        )
