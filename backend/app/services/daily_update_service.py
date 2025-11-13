"""
每日数据更新服务
负责执行定时任务中的各种数据更新逻辑
"""

from datetime import datetime
from app.utils.logger import get_logger
from app.services.stock_service import StockInfoService

logger = get_logger(__name__)


class DailyUpdateService:
    """每日数据更新服务类"""

    def __init__(self):
        self.stock_service = StockInfoService()

    def update_all_stocks_info(self):
        """
        更新所有股票的基础信息

        功能：
        1. 从 AkShare 获取所有 A 股列表
        2. 对比数据库中已有的股票
        3. 新增不存在的股票
        4. 更新已存在股票的基础信息

        Returns:
            dict: {
                'total': 总数,
                'added': 新增数量,
                'updated': 更新数量,
                'failed': 失败数量,
                'error_codes': 失败的股票代码列表
            }
        """
        logger.info("开始更新所有股票基础信息...")

        # 统计信息
        stats = {'total': 0, 'added': 0, 'updated': 0, 'failed': 0, 'error_codes': []}

        try:
            # 1. 获取所有A股列表
            logger.info("正在从 AkShare 获取股票列表...")
            stock_list = self.stock_service._fetch_from_akshare('stock_info_a_code_name')

            if not stock_list:
                logger.error("无法获取股票列表")
                return stats

            stats['total'] = len(stock_list)
            logger.info(f"获取到 {stats['total']} 只股票")

            # 2. 遍历处理每只股票
            for idx, stock_data in enumerate(stock_list, 1):
                code = stock_data.get('code')
                name = stock_data.get('name')

                if not code:
                    continue

                try:
                    # 检查是否已存在
                    existing_stock = self.stock_service.get_stock_by_code(code)

                    if existing_stock:
                        # 更新现有股票的名称（如果有变化）
                        if existing_stock.name != name:
                            existing_stock.name = name
                            existing_stock.updated_at = datetime.now()
                            stats['updated'] += 1
                            logger.debug(f"更新股票: {code} - {name}")
                    else:
                        # 新增股票（调用现有的 add_stock_by_code 方法获取详细信息）
                        logger.info(f"发现新股票: {code} - {name}，正在获取详细信息...")
                        result = self.stock_service.add_stock_by_code(code)

                        if result:
                            stats['added'] += 1
                            logger.info(f"成功添加新股票: {code} - {name}")
                        else:
                            stats['failed'] += 1
                            stats['error_codes'].append(code)
                            logger.warning(f"添加股票失败: {code} - {name}")

                    # 每处理100只股票提交一次并记录进度
                    if idx % 100 == 0:
                        db.session.commit()
                        logger.info(
                            f"进度: {idx}/{stats['total']} "
                            f"(新增: {stats['added']}, 更新: {stats['updated']}, 失败: {stats['failed']})"
                        )

                except Exception as e:
                    logger.error(f"处理股票 {code} 时出错: {str(e)}")
                    stats['failed'] += 1
                    stats['error_codes'].append(code)
                    db.session.rollback()  # 回滚当前失败的操作
                    continue

            # 3. 最终提交
            db.session.commit()

            logger.info(
                f"股票信息更新完成 - "
                f"总数: {stats['total']}, "
                f"新增: {stats['added']}, "
                f"更新: {stats['updated']}, "
                f"失败: {stats['failed']}"
            )

            if stats['error_codes']:
                logger.warning(f"失败的股票代码: {stats['error_codes'][:10]}...")  # 只显示前10个

        except Exception as e:
            db.session.rollback()
            logger.error(f"批量更新股票信息失败: {str(e)}", exc_info=True)
            raise

        return stats

    def execute_daily_updates(self):
        """
        执行所有每日更新任务

        Returns:
            dict: 所有更新任务的结果汇总
        """
        logger.info("开始执行每日数据更新任务...")

        results = {'start_time': datetime.now().isoformat(), 'tasks': {}}

        return results
