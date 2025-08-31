"""
工作流管理器

统一管理和协调所有数据工作流。
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..collectors.base_collector import BaseCollector
from ..collectors.tushare_collector import TushareCollector
from ..collectors.akshare_collector import AKShareCollector
from ..collectors.yfinance_collector import YFinanceCollector
from ..storage.stock_storage import StockInfoStorage
from .stock_workflow import StockWorkflow
from ...utils.logger import get_logger
from ...utils.config import ConfigManager


class WorkflowManager:
    """工作流管理器"""

    def __init__(self):
        """初始化工作流管理器"""
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        self.collectors: Dict[str, BaseCollector] = {}
        self.storage: Optional[StockInfoStorage] = None
        self.stock_workflow: Optional[StockWorkflow] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """
        初始化工作流管理器

        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("开始初始化工作流管理器")

            # 初始化数据收集器
            await self._initialize_collectors()

            # 初始化存储器
            await self._initialize_storage()

            # 初始化工作流
            await self._initialize_workflows()

            self._initialized = True
            self.logger.info("工作流管理器初始化完成")
            return True

        except Exception as e:
            self.logger.error(f"工作流管理器初始化失败: {e}")
            return False

    async def _initialize_collectors(self):
        """初始化数据收集器"""
        self.logger.info("初始化数据收集器")

        # 初始化Tushare收集器
        try:
            tushare_collector = TushareCollector()
            self.collectors['tushare'] = tushare_collector
            self.logger.info("Tushare收集器初始化成功")
        except Exception as e:
            self.logger.warning(f"Tushare收集器初始化失败: {e}")

        # 初始化AKShare收集器
        try:
            akshare_collector = AKShareCollector()
            self.collectors['akshare'] = akshare_collector
            self.logger.info("AKShare收集器初始化成功")
        except Exception as e:
            self.logger.warning(f"AKShare收集器初始化失败: {e}")

        # 初始化yfinance收集器
        try:
            yfinance_collector = YFinanceCollector()
            self.collectors['yfinance'] = yfinance_collector
            self.logger.info("yfinance收集器初始化成功")
        except Exception as e:
            self.logger.warning(f"yfinance收集器初始化失败: {e}")

        if not self.collectors:
            raise Exception("没有可用的数据收集器")

        self.logger.info(f"成功初始化 {len(self.collectors)} 个数据收集器")

    async def _initialize_storage(self):
        """初始化存储器"""
        self.logger.info("初始化存储器")

        try:
            self.storage = StockInfoStorage()
            self.logger.info("存储器初始化成功")
        except Exception as e:
            self.logger.error(f"存储器初始化失败: {e}")
            raise

    async def _initialize_workflows(self):
        """初始化工作流"""
        self.logger.info("初始化工作流")

        if not self.collectors or not self.storage:
            raise Exception("收集器或存储器未初始化")

        self.stock_workflow = StockWorkflow(self.collectors, self.storage)
        self.logger.info("股票工作流初始化成功")

    async def run_stock_info_collection(
        self,
        symbols: Optional[List[str]] = None,
        market: str = 'all',
        preferred_collector: Optional[str] = None,
        batch_size: int = 50,
    ) -> Dict[str, Any]:
        """
        运行股票基本信息收集工作流

        Args:
            symbols: 指定的股票代码列表，如果为None则获取市场上所有股票
            market: 市场类型 ('sh', 'sz', 'all')
            preferred_collector: 首选收集器
            batch_size: 批处理大小

        Returns:
            Dict: 处理结果统计
        """
        if not self._initialized:
            raise Exception("工作流管理器未初始化")

        self.logger.info("开始运行股票基本信息收集工作流")

        try:
            if symbols is None:
                # 如果没有指定股票列表，则更新整个市场的股票列表
                result = await self.stock_workflow.update_stock_list(market)
            else:
                # 收集指定股票的信息
                result = await self.stock_workflow.collect_and_store_stock_info(
                    symbols, preferred_collector, batch_size
                )

            self.logger.info("股票基本信息收集工作流完成")
            return result

        except Exception as e:
            self.logger.error(f"股票基本信息收集工作流失败: {e}")
            raise

    async def run_historical_data_collection(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        preferred_collector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        运行历史数据收集工作流

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            preferred_collector: 首选收集器

        Returns:
            Dict: 处理结果统计
        """
        if not self._initialized:
            raise Exception("工作流管理器未初始化")

        self.logger.info("开始运行历史数据收集工作流")

        try:
            result = await self.stock_workflow.collect_and_store_historical_data(
                symbols, start_date, end_date, preferred_collector
            )

            self.logger.info("历史数据收集工作流完成")
            return result

        except Exception as e:
            self.logger.error(f"历史数据收集工作流失败: {e}")
            raise

    async def run_daily_update(self) -> Dict[str, Any]:
        """
        运行每日数据更新工作流

        Returns:
            Dict: 处理结果统计
        """
        if not self._initialized:
            raise Exception("工作流管理器未初始化")

        self.logger.info("开始运行每日数据更新工作流")

        try:
            # 获取现有股票列表
            existing_stocks = self.storage.list_all_symbols()

            if not existing_stocks:
                self.logger.warning("数据库中没有股票数据，先运行完整更新")
                return await self.run_stock_info_collection()

            # 更新现有股票的基本信息
            result = await self.stock_workflow.collect_and_store_stock_info(existing_stocks, batch_size=20)

            # TODO: 这里可以扩展为同时更新历史数据
            # 获取最新的交易日数据
            # today = datetime.now()
            # yesterday = today - timedelta(days=1)
            # await self.run_historical_data_collection(existing_stocks[:10], yesterday, today)

            self.logger.info("每日数据更新工作流完成")
            return result

        except Exception as e:
            self.logger.error(f"每日数据更新工作流失败: {e}")
            raise

    async def run_full_update(self, market: str = 'all') -> Dict[str, Any]:
        """
        运行完整数据更新工作流

        Args:
            market: 市场类型

        Returns:
            Dict: 处理结果统计
        """
        if not self._initialized:
            raise Exception("工作流管理器未初始化")

        self.logger.info("开始运行完整数据更新工作流")

        try:
            # 更新股票列表和基本信息
            result = await self.stock_workflow.update_stock_list(market)

            self.logger.info("完整数据更新工作流完成")
            return result

        except Exception as e:
            self.logger.error(f"完整数据更新工作流失败: {e}")
            raise

    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态

        Returns:
            Dict: 系统状态信息
        """
        return {
            'initialized': self._initialized,
            'collectors': {
                name: collector.is_available() if hasattr(collector, 'is_available') else True
                for name, collector in self.collectors.items()
            },
            'storage_connected': self.storage.is_connected() if self.storage else False,
            'workflows': {'stock_workflow': self.stock_workflow is not None},
            'timestamp': datetime.now().isoformat(),
        }

    async def cleanup(self):
        """清理资源"""
        self.logger.info("开始清理工作流管理器资源")

        try:
            # 清理收集器
            for name, collector in self.collectors.items():
                if hasattr(collector, 'cleanup'):
                    await collector.cleanup()
                    self.logger.debug(f"清理收集器 {name}")

            # 清理存储器
            if self.storage and hasattr(self.storage, 'cleanup'):
                await self.storage.cleanup()
                self.logger.debug("清理存储器")

            self._initialized = False
            self.logger.info("工作流管理器资源清理完成")

        except Exception as e:
            self.logger.error(f"清理资源时发生错误: {e}")
