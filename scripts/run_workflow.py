"""
工作流运行脚本

演示如何使用数据收集到存储的完整工作流。
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.workflows.workflow_manager import WorkflowManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def demo_stock_info_workflow():
    """演示股票基本信息收集工作流"""
    print("\n=== 股票基本信息收集工作流演示 ===")

    workflow_manager = WorkflowManager()

    try:
        # 初始化工作流管理器
        print("1. 初始化工作流管理器...")
        success = await workflow_manager.initialize()
        if not success:
            print("❌ 工作流管理器初始化失败")
            return
        print("✅ 工作流管理器初始化成功")

        # 检查系统状态
        print("\n2. 检查系统状态...")
        status = workflow_manager.get_system_status()
        print(f"   - 收集器状态: {status['collectors']}")
        print(f"   - 存储器连接: {status['storage_connected']}")
        print(f"   - 工作流状态: {status['workflows']}")

        # 收集指定股票的基本信息
        print("\n3. 收集指定股票的基本信息...")
        test_symbols = ['000001.SZ', '600000.SH', '000002.SZ', '600519.SH', '000858.SZ']

        result = await workflow_manager.run_stock_info_collection(
            symbols=test_symbols, preferred_collector='tushare', batch_size=2  # 优先使用Tushare  # 小批量测试
        )

        print(f"   - 处理结果:")
        print(f"     总数: {result['total']}")
        print(f"     成功: {result['success']}")
        print(f"     失败: {result['failed']}")
        if result['errors']:
            print(f"     错误: {result['errors'][:3]}...")  # 只显示前3个错误

        print("\n✅ 股票基本信息收集工作流演示完成")

    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        logger.error(f"工作流执行失败: {e}")

    finally:
        # 清理资源
        await workflow_manager.cleanup()
        print("🧹 资源清理完成")


async def demo_historical_data_workflow():
    """演示历史数据收集工作流"""
    print("\n=== 历史数据收集工作流演示 ===")

    workflow_manager = WorkflowManager()

    try:
        print("1. 初始化工作流管理器...")
        success = await workflow_manager.initialize()
        if not success:
            print("❌ 工作流管理器初始化失败")
            return
        print("✅ 工作流管理器初始化成功")

        # 收集历史数据
        print("\n2. 收集历史数据...")
        test_symbols = ['000001.SZ', '600000.SH']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # 最近一周的数据

        result = await workflow_manager.run_historical_data_collection(
            symbols=test_symbols, start_date=start_date, end_date=end_date, preferred_collector='yfinance'
        )

        print(f"   - 处理结果:")
        print(f"     总数: {result['total']}")
        print(f"     成功: {result['success']}")
        print(f"     失败: {result['failed']}")
        if result['errors']:
            print(f"     错误: {result['errors'][:3]}...")

        print("\n✅ 历史数据收集工作流演示完成")

    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        logger.error(f"工作流执行失败: {e}")

    finally:
        await workflow_manager.cleanup()
        print("🧹 资源清理完成")


async def demo_daily_update_workflow():
    """演示每日更新工作流"""
    print("\n=== 每日更新工作流演示 ===")

    workflow_manager = WorkflowManager()

    try:
        print("1. 初始化工作流管理器...")
        success = await workflow_manager.initialize()
        if not success:
            print("❌ 工作流管理器初始化失败")
            return
        print("✅ 工作流管理器初始化成功")

        print("\n2. 运行每日更新...")
        result = await workflow_manager.run_daily_update()

        print(f"   - 处理结果:")
        print(f"     总数: {result['total']}")
        print(f"     成功: {result['success']}")
        print(f"     失败: {result['failed']}")

        print("\n✅ 每日更新工作流演示完成")

    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        logger.error(f"工作流执行失败: {e}")

    finally:
        await workflow_manager.cleanup()
        print("🧹 资源清理完成")


async def main():
    """主函数"""
    print("🚀 MarketSeer 数据工作流演示")
    print("=" * 50)

    try:
        # 1. 演示股票基本信息收集工作流
        await demo_stock_info_workflow()

        # 等待一下，避免过于频繁的请求
        print("\n⏱️  等待 3 秒...")
        await asyncio.sleep(3)

        # 2. 演示历史数据收集工作流
        await demo_historical_data_workflow()

        # 等待一下
        print("\n⏱️  等待 3 秒...")
        await asyncio.sleep(3)

        # 3. 演示每日更新工作流
        await demo_daily_update_workflow()

        print("\n🎉 所有工作流演示完成！")

    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        logger.error(f"演示过程中发生错误: {e}")


if __name__ == "__main__":
    # 设置事件循环策略（Windows系统需要）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # 运行演示
    asyncio.run(main())
