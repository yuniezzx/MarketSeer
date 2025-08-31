"""
股票数据工作流管理器

提供股票数据从收集到存储的完整工作流管理功能。
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from ..collectors.base_collector import BaseCollector
from ..collectors.data_types import StockInfo, HistoricalData, RealtimeData, FinancialData
from ..collectors.exceptions import DataCollectorError, RateLimitError, SymbolNotFoundError
from ..storage.stock_storage import StockInfoStorage
from ...utils.logger import get_logger
from ...utils.config import ConfigManager


class StockWorkflow:
    """股票数据工作流管理器"""

    def __init__(self, collectors: Dict[str, BaseCollector], storage: StockInfoStorage):
        """
        初始化工作流管理器

        Args:
            collectors: 数据收集器字典，key为收集器名称
            storage: 股票信息存储器
        """
        self.collectors = collectors
        self.storage = storage
        self.logger = get_logger(__name__)
        self.config = ConfigManager()

    async def collect_and_store_stock_info(
        self, symbols: List[str], preferred_collector: Optional[str] = None, batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        收集并存储股票基本信息

        Args:
            symbols: 股票代码列表
            preferred_collector: 首选数据收集器名称
            batch_size: 批处理大小

        Returns:
            Dict: 处理结果统计
        """
        self.logger.info(f"开始收集并存储股票基本信息，共 {len(symbols)} 只股票")

        results = {'total': len(symbols), 'success': 0, 'failed': 0, 'errors': []}

        # 分批处理
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i : i + batch_size]
            self.logger.info(f"处理第 {i//batch_size + 1} 批，共 {len(batch_symbols)} 只股票")

            batch_results = await self._process_stock_info_batch(batch_symbols, preferred_collector)

            # 合并结果
            results['success'] += batch_results['success']
            results['failed'] += batch_results['failed']
            results['errors'].extend(batch_results['errors'])

            # 批次间延迟，避免过于频繁的请求
            if i + batch_size < len(symbols):
                await asyncio.sleep(1)

        self.logger.info(f"股票基本信息收集完成：成功 {results['success']}，失败 {results['failed']}")
        return results

    async def _process_stock_info_batch(
        self, symbols: List[str], preferred_collector: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理一批股票基本信息"""

        results = {'success': 0, 'failed': 0, 'errors': []}

        stock_infos = []

        for symbol in symbols:
            try:
                stock_info = await self._collect_stock_info(symbol, preferred_collector)
                if stock_info:
                    stock_infos.append(stock_info)
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{symbol}: 未找到数据")

            except Exception as e:
                self.logger.error(f"收集股票 {symbol} 信息失败: {e}")
                results['failed'] += 1
                results['errors'].append(f"{symbol}: {str(e)}")

        # 批量存储
        if stock_infos:
            try:
                self.storage.batch_insert(stock_infos)
                self.logger.info(f"成功存储 {len(stock_infos)} 只股票信息")
            except Exception as e:
                self.logger.error(f"批量存储失败: {e}")
                # 如果批量存储失败，尝试逐个存储
                await self._fallback_individual_storage(stock_infos)

        return results

    async def _collect_stock_info(
        self, symbol: str, preferred_collector: Optional[str] = None
    ) -> Optional[StockInfo]:
        """
        收集单只股票的基本信息

        Args:
            symbol: 股票代码
            preferred_collector: 首选收集器

        Returns:
            StockInfo: 股票信息对象，如果失败返回None
        """
        collectors_to_try = []

        # 如果指定了首选收集器，优先使用
        if preferred_collector and preferred_collector in self.collectors:
            collectors_to_try.append(preferred_collector)

        # 添加其他收集器作为备选
        for name in self.collectors:
            if name not in collectors_to_try:
                collectors_to_try.append(name)

        last_error = None

        for collector_name in collectors_to_try:
            try:
                collector = self.collectors[collector_name]
                self.logger.debug(f"使用 {collector_name} 收集器获取 {symbol} 信息")

                stock_info = await collector.get_stock_info(symbol)
                if stock_info:
                    self.logger.debug(f"成功从 {collector_name} 获取 {symbol} 信息")
                    return stock_info

            except RateLimitError as e:
                self.logger.warning(f"收集器 {collector_name} 触发限频: {e}")
                last_error = e
                # 等待一段时间后重试
                await asyncio.sleep(5)
                continue

            except SymbolNotFoundError as e:
                self.logger.debug(f"收集器 {collector_name} 未找到 {symbol} 数据: {e}")
                last_error = e
                continue

            except DataCollectorError as e:
                self.logger.warning(f"收集器 {collector_name} 错误: {e}")
                last_error = e
                continue

            except Exception as e:
                self.logger.error(f"收集器 {collector_name} 未预期错误: {e}")
                last_error = e
                continue

        self.logger.warning(f"所有收集器都无法获取 {symbol} 信息，最后错误: {last_error}")
        return None

    async def _fallback_individual_storage(self, stock_infos: List[StockInfo]):
        """批量存储失败时的回退方案：逐个存储"""
        self.logger.info("批量存储失败，尝试逐个存储")

        success_count = 0
        for stock_info in stock_infos:
            try:
                self.storage.insert(stock_info)
                success_count += 1
            except Exception as e:
                self.logger.error(f"存储股票 {stock_info.symbol} 失败: {e}")

        self.logger.info(f"逐个存储完成，成功 {success_count}/{len(stock_infos)}")

    async def collect_and_store_historical_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        preferred_collector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        收集并存储历史数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            preferred_collector: 首选收集器

        Returns:
            Dict: 处理结果统计
        """
        self.logger.info(f"开始收集历史数据：{start_date} 到 {end_date}，共 {len(symbols)} 只股票")

        results = {'total': len(symbols), 'success': 0, 'failed': 0, 'errors': []}

        for symbol in symbols:
            try:
                # 收集历史数据
                historical_data = await self._collect_historical_data(
                    symbol, start_date, end_date, preferred_collector
                )

                if historical_data and not historical_data.data.empty:
                    # 这里可以扩展为存储到历史数据表
                    # 目前先保存到文件
                    await self._save_historical_data_to_file(symbol, historical_data)
                    results['success'] += 1
                    self.logger.debug(f"成功收集并保存 {symbol} 历史数据")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{symbol}: 未获取到历史数据")

            except Exception as e:
                self.logger.error(f"处理 {symbol} 历史数据失败: {e}")
                results['failed'] += 1
                results['errors'].append(f"{symbol}: {str(e)}")

        self.logger.info(f"历史数据收集完成：成功 {results['success']}，失败 {results['failed']}")
        return results

    async def _collect_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime, preferred_collector: Optional[str] = None
    ) -> Optional[HistoricalData]:
        """收集单只股票的历史数据"""

        collectors_to_try = []

        if preferred_collector and preferred_collector in self.collectors:
            collectors_to_try.append(preferred_collector)

        for name in self.collectors:
            if name not in collectors_to_try:
                collectors_to_try.append(name)

        for collector_name in collectors_to_try:
            try:
                collector = self.collectors[collector_name]
                historical_data = await collector.get_historical_data(symbol, start_date, end_date)
                if historical_data and not historical_data.data.empty:
                    return historical_data

            except Exception as e:
                self.logger.warning(f"收集器 {collector_name} 获取 {symbol} 历史数据失败: {e}")
                continue

        return None

    async def _save_historical_data_to_file(self, symbol: str, data: HistoricalData):
        """保存历史数据到文件"""
        import os

        # 创建数据目录
        data_dir = "data/processed/historical"
        os.makedirs(data_dir, exist_ok=True)

        # 保存为CSV文件
        file_path = f"{data_dir}/{symbol}_{data.start_date}_{data.end_date}.csv"
        data.data.to_csv(file_path, index=False, encoding='utf-8-sig')

        self.logger.debug(f"历史数据保存到: {file_path}")

    async def update_stock_list(self, market: str = 'all') -> Dict[str, Any]:
        """
        更新股票列表

        Args:
            market: 市场类型 ('sh', 'sz', 'all')

        Returns:
            Dict: 更新结果统计
        """
        self.logger.info(f"开始更新股票列表，市场: {market}")

        # 获取股票列表
        stock_symbols = await self._get_stock_list(market)

        if not stock_symbols:
            self.logger.warning("未获取到股票列表")
            return {'total': 0, 'success': 0, 'failed': 0, 'errors': ['未获取到股票列表']}

        # 收集并存储股票信息
        return await self.collect_and_store_stock_info(stock_symbols)

    async def _get_stock_list(self, market: str = 'all') -> List[str]:
        """获取股票列表"""

        for collector_name, collector in self.collectors.items():
            try:
                # 这里需要根据具体的收集器实现来获取股票列表
                # 暂时返回一个示例列表
                if hasattr(collector, 'get_stock_list'):
                    stock_list = await collector.get_stock_list(market)
                    if stock_list:
                        self.logger.info(f"从 {collector_name} 获取到 {len(stock_list)} 只股票")
                        return stock_list

            except Exception as e:
                self.logger.warning(f"从 {collector_name} 获取股票列表失败: {e}")
                continue

        # 如果所有收集器都失败，返回一些示例股票代码
        self.logger.warning("所有收集器获取股票列表失败，返回示例列表")
        return [
            '000001.SZ',
            '000002.SZ',
            '600000.SH',
            '600519.SH',
            '000858.SZ',
            '002415.SZ',
            '300059.SZ',
            '600036.SH',
            '000166.SZ',
            '002594.SZ',
        ]

    def get_workflow_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            'collectors': list(self.collectors.keys()),
            'storage_connected': self.storage.is_connected(),
            'timestamp': datetime.now().isoformat(),
        }
