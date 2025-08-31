"""
工作流模块测试

测试数据收集到存储的完整工作流功能。
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.workflows.workflow_manager import WorkflowManager
from src.data.workflows.stock_workflow import StockWorkflow
from src.data.collectors.data_types import StockInfo, HistoricalData
import pandas as pd


class TestStockWorkflow:
    """股票工作流测试类"""

    @pytest.fixture
    async def mock_collectors(self):
        """模拟收集器"""
        mock_collector = AsyncMock()
        mock_collector.get_stock_info.return_value = StockInfo(
            symbol='000001.SZ',
            name='平安银行',
            exchange='深交所',
            market='主板',
            listing_date=datetime(1991, 4, 3),
            industry='银行',
            sector='金融业',
            market_cap=1500000000000.0,
            pe_ratio=5.2,
            pb_ratio=0.8,
        )

        # 模拟历史数据
        mock_data = pd.DataFrame(
            {
                'date': ['2024-01-01', '2024-01-02'],
                'open': [10.0, 10.5],
                'high': [10.5, 11.0],
                'low': [9.8, 10.2],
                'close': [10.3, 10.8],
                'volume': [1000000, 1200000],
            }
        )

        mock_collector.get_historical_data.return_value = HistoricalData(
            symbol='000001.SZ', start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 2), data=mock_data
        )

        return {'mock_collector': mock_collector}

    @pytest.fixture
    async def mock_storage(self):
        """模拟存储器"""
        mock_storage = AsyncMock()
        mock_storage.is_connected.return_value = True
        mock_storage.batch_insert.return_value = None
        mock_storage.insert.return_value = None
        mock_storage.list_all_symbols.return_value = ['000001.SZ', '600000.SH']
        return mock_storage

    @pytest.fixture
    async def stock_workflow(self, mock_collectors, mock_storage):
        """创建股票工作流实例"""
        return StockWorkflow(mock_collectors, mock_storage)

    @pytest.mark.asyncio
    async def test_collect_and_store_stock_info(self, stock_workflow):
        """测试收集并存储股票基本信息"""
        symbols = ['000001.SZ', '000002.SZ']

        result = await stock_workflow.collect_and_store_stock_info(symbols, batch_size=1)

        assert result['total'] == 2
        assert result['success'] >= 0
        assert result['failed'] >= 0
        assert isinstance(result['errors'], list)

    @pytest.mark.asyncio
    async def test_collect_historical_data(self, stock_workflow):
        """测试收集历史数据"""
        symbols = ['000001.SZ']
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)

        result = await stock_workflow.collect_and_store_historical_data(symbols, start_date, end_date)

        assert result['total'] == 1
        assert result['success'] >= 0
        assert result['failed'] >= 0

    @pytest.mark.asyncio
    async def test_update_stock_list(self, stock_workflow):
        """测试更新股票列表"""
        result = await stock_workflow.update_stock_list()

        assert 'total' in result
        assert 'success' in result
        assert 'failed' in result
        assert 'errors' in result

    def test_get_workflow_status(self, stock_workflow):
        """测试获取工作流状态"""
        status = stock_workflow.get_workflow_status()

        assert 'collectors' in status
        assert 'storage_connected' in status
        assert 'timestamp' in status


class TestWorkflowManager:
    """工作流管理器测试类"""

    @pytest.fixture
    async def workflow_manager(self):
        """创建工作流管理器实例"""
        return WorkflowManager()

    @pytest.mark.asyncio
    async def test_initialization(self, workflow_manager):
        """测试初始化"""
        # 这个测试需要真实的数据库连接，所以我们模拟它
        with patch.object(workflow_manager, '_initialize_collectors') as mock_init_collectors, patch.object(
            workflow_manager, '_initialize_storage'
        ) as mock_init_storage, patch.object(
            workflow_manager, '_initialize_workflows'
        ) as mock_init_workflows:

            mock_init_collectors.return_value = None
            mock_init_storage.return_value = None
            mock_init_workflows.return_value = None

            success = await workflow_manager.initialize()
            assert success is True
            assert workflow_manager._initialized is True

    def test_get_system_status_not_initialized(self, workflow_manager):
        """测试未初始化状态下的系统状态"""
        status = workflow_manager.get_system_status()

        assert status['initialized'] is False
        assert status['storage_connected'] is False
        assert status['workflows']['stock_workflow'] is False

    @pytest.mark.asyncio
    async def test_run_stock_info_collection_not_initialized(self, workflow_manager):
        """测试未初始化时运行股票信息收集"""
        with pytest.raises(Exception, match="工作流管理器未初始化"):
            await workflow_manager.run_stock_info_collection(['000001.SZ'])

    @pytest.mark.asyncio
    async def test_run_historical_data_collection_not_initialized(self, workflow_manager):
        """测试未初始化时运行历史数据收集"""
        with pytest.raises(Exception, match="工作流管理器未初始化"):
            await workflow_manager.run_historical_data_collection(
                ['000001.SZ'], datetime.now(), datetime.now()
            )

    @pytest.mark.asyncio
    async def test_run_daily_update_not_initialized(self, workflow_manager):
        """测试未初始化时运行每日更新"""
        with pytest.raises(Exception, match="工作流管理器未初始化"):
            await workflow_manager.run_daily_update()

    @pytest.mark.asyncio
    async def test_cleanup(self, workflow_manager):
        """测试资源清理"""
        # 模拟已初始化的状态
        workflow_manager._initialized = True
        workflow_manager.collectors = {'test': Mock()}
        workflow_manager.storage = Mock()

        await workflow_manager.cleanup()

        assert workflow_manager._initialized is False


class TestWorkflowIntegration:
    """工作流集成测试"""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow_mock(self):
        """端到端工作流测试（使用模拟）"""
        # 创建模拟的收集器和存储器
        mock_collector = AsyncMock()
        mock_collector.initialize.return_value = None
        mock_collector.get_stock_info.return_value = StockInfo(
            symbol='000001.SZ',
            name='平安银行',
            exchange='深交所',
            market='主板',
            listing_date=datetime(1991, 4, 3),
            industry='银行',
            sector='金融业',
        )

        mock_storage = AsyncMock()
        mock_storage.initialize.return_value = None
        mock_storage.is_connected.return_value = True
        mock_storage.batch_insert.return_value = None
        mock_storage.list_all_symbols.return_value = []

        # 创建工作流
        workflow = StockWorkflow({'mock': mock_collector}, mock_storage)

        # 执行工作流
        result = await workflow.collect_and_store_stock_info(['000001.SZ'])

        # 验证结果
        assert result['total'] == 1
        assert result['success'] >= 0

        # 验证调用
        mock_collector.get_stock_info.assert_called()
        mock_storage.batch_insert.assert_called()

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """测试工作流错误处理"""
        # 创建会抛出异常的模拟收集器
        mock_collector = AsyncMock()
        mock_collector.get_stock_info.side_effect = Exception("网络错误")

        mock_storage = AsyncMock()
        mock_storage.is_connected.return_value = True

        workflow = StockWorkflow({'mock': mock_collector}, mock_storage)

        # 执行工作流
        result = await workflow.collect_and_store_stock_info(['000001.SZ'])

        # 验证错误被正确处理
        assert result['total'] == 1
        assert result['failed'] == 1
        assert len(result['errors']) == 1
        assert "网络错误" in result['errors'][0]

    @pytest.mark.asyncio
    async def test_workflow_fallback_storage(self):
        """测试工作流存储回退机制"""
        mock_collector = AsyncMock()
        mock_collector.get_stock_info.return_value = StockInfo(
            symbol='000001.SZ',
            name='平安银行',
            exchange='深交所',
            market='主板',
            listing_date=datetime(1991, 4, 3),
            industry='银行',
            sector='金融业',
        )

        mock_storage = AsyncMock()
        mock_storage.is_connected.return_value = True
        # 批量存储失败
        mock_storage.batch_insert.side_effect = Exception("批量插入失败")
        # 单个存储成功
        mock_storage.insert.return_value = None

        workflow = StockWorkflow({'mock': mock_collector}, mock_storage)

        result = await workflow.collect_and_store_stock_info(['000001.SZ'])

        # 验证回退机制被调用
        mock_storage.batch_insert.assert_called_once()
        mock_storage.insert.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
