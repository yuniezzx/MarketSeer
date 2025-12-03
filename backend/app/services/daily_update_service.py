"""
日常数据更新服务
负责定时采集和更新龙虎榜等数据
"""

from app.models import DailyLHB
from .base_service import BaseService
from app.mapping import weekly_lhb_mapper
from app.utils import get_current_time


class DailyUpdateService(BaseService):
    """日常数据更新服务"""

    def update_daily_lhb(self):
        """
        更新周龙虎榜数据，调用 akshare 的 stock_lhb_detail_em 接口
        """
        # 获取当前日期，格式化为 YYYYMMDD
        current_date = get_current_time(fmt='%Y%m%d')

        # 从 AkShare 获取龙虎榜数据，传入日期参数
        lhb_data = self._fetch_from_akshare(
            'stock_lhb_detail_em', api_params={'start_date': current_date, 'end_date': current_date}
        )
        if not lhb_data:
            self.logger.warning("未获取到龙虎榜数据")
            return 0

        # 数据映射处理
        mapped_data = [weekly_lhb_mapper(item) for item in lhb_data]

        # 保存到数据库
        updated_count = self._save_to_db(DailyLHB, mapped_data, unique_field='code')
        self.logger.info(f"龙虎榜数据更新完成，更新记录数: {updated_count}")
        return updated_count
