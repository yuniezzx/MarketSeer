"""
股票信息存储服务测试

测试股票基本信息的存储、查询、更新等功能
"""

import sys
import os
from datetime import datetime, date
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.storage.stock_storage import StockInfoStorage
from src.data.storage.database import DatabaseManager
from src.data.collectors.data_types import StockInfo
from src.data.collectors import get_tushare_collector, get_akshare_collector
from src.utils.logger import get_database_logger


def test_database_connection():
    """测试数据库连接"""
    print("🔗 测试数据库连接...")

    try:
        db_manager = DatabaseManager()

        # 测试连接
        result = db_manager.fetch_one("SELECT 1 as test")
        if result and result['test'] == 1:
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接失败")
            return False

    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def test_create_table():
    """测试创建股票表"""
    print("🏗️  测试创建股票表...")

    try:
        db_manager = DatabaseManager()

        # 读取SQL文件
        sql_file = Path("scripts/create_stocks_table.sql")
        if not sql_file.exists():
            print("❌ SQL文件不存在")
            return False

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 执行建表语句（忽略表已存在的错误）
        try:
            # 先删除表（如果存在）
            db_manager.execute("DROP TABLE IF EXISTS stocks")

            # 创建表
            db_manager.execute(sql_content)
            print("✅ 股票表创建成功")
            return True

        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            return False

    except Exception as e:
        print(f"❌ 创建表过程错误: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def test_stock_storage_basic():
    """测试股票存储基本功能"""
    print("💾 测试股票存储基本功能...")

    try:
        storage = StockInfoStorage()

        # 创建测试股票信息
        test_stock = StockInfo(
            symbol="000001.SZ",
            name="平安银行",
            exchange="SZSE",
            market="主板",
            industry="银行",
            sector="金融",
            list_date=date(1991, 4, 3),
            is_active=True,
            currency="CNY",
            market_cap=300000000000,
            shares_outstanding=19405918198,
            description="中国平安保险（集团）股份有限公司控股的全国性股份制商业银行",
            website="https://bank.pingan.com",
        )

        # 测试保存
        print("  📝 测试保存股票信息...")
        success = storage.save_stock_info(test_stock)
        if success:
            print("  ✅ 保存成功")
        else:
            print("  ❌ 保存失败")
            return False

        # 测试查询
        print("  🔍 测试查询股票信息...")
        retrieved_stock = storage.get_stock_info("000001.SZ")
        if retrieved_stock:
            print(f"  ✅ 查询成功: {retrieved_stock.name}")

            # 验证数据完整性
            assert retrieved_stock.symbol == test_stock.symbol
            assert retrieved_stock.name == test_stock.name
            assert retrieved_stock.exchange == test_stock.exchange
            print("  ✅ 数据完整性验证通过")
        else:
            print("  ❌ 查询失败")
            return False

        # 测试更新
        print("  🔄 测试更新股票信息...")
        test_stock.market_cap = 350000000000  # 更新市值
        test_stock.description = "更新后的描述"

        update_success = storage.update_stock_info("000001.SZ", test_stock)
        if update_success:
            print("  ✅ 更新成功")

            # 验证更新
            updated_stock = storage.get_stock_info("000001.SZ")
            if updated_stock and updated_stock.market_cap == 350000000000:
                print("  ✅ 更新验证通过")
            else:
                print("  ❌ 更新验证失败")
                return False
        else:
            print("  ❌ 更新失败")
            return False

        # 测试搜索
        print("  🔎 测试搜索功能...")
        search_results = storage.search_stocks(name_pattern="平安", limit=10)
        if search_results and len(search_results) > 0:
            print(f"  ✅ 搜索成功，找到 {len(search_results)} 条记录")
        else:
            print("  ❌ 搜索失败")

        # 测试统计
        print("  📊 测试统计功能...")
        count = storage.get_stock_count()
        print(f"  ✅ 数据库中共有 {count} 只股票")

        return True

    except Exception as e:
        print(f"❌ 股票存储测试失败: {e}")
        return False
    finally:
        if 'storage' in locals():
            storage.close()


def test_batch_operations():
    """测试批量操作"""
    print("📦 测试批量操作...")

    try:
        storage = StockInfoStorage()

        # 创建测试股票列表
        test_stocks = [
            StockInfo(
                symbol="000002.SZ",
                name="万科A",
                exchange="SZSE",
                market="主板",
                industry="房地产",
                currency="CNY",
            ),
            StockInfo(
                symbol="600000.SS",
                name="浦发银行",
                exchange="SSE",
                market="主板",
                industry="银行",
                currency="CNY",
            ),
            StockInfo(
                symbol="300001.SZ",
                name="特锐德",
                exchange="SZSE",
                market="创业板",
                industry="电力设备",
                currency="CNY",
            ),
        ]

        # 测试批量保存
        print("  📝 测试批量保存...")
        result = storage.batch_save_stocks(test_stocks, backup=False)  # 关闭备份以加快测试

        print(f"  📊 批量保存结果:")
        print(f"    总计: {result['total']}")
        print(f"    成功: {result['success']}")
        print(f"    失败: {result['failed']}")

        if result['failed'] > 0:
            print(f"    失败股票: {result['failed_symbols']}")

        if result['success'] == len(test_stocks):
            print("  ✅ 批量保存完全成功")
        else:
            print("  ⚠️  批量保存部分成功")

        # 验证批量保存的数据
        print("  🔍 验证批量保存的数据...")
        for stock in test_stocks:
            retrieved = storage.get_stock_info(stock.symbol)
            if retrieved:
                print(f"    ✅ {stock.symbol} - {retrieved.name}")
            else:
                print(f"    ❌ {stock.symbol} - 未找到")

        return True

    except Exception as e:
        print(f"❌ 批量操作测试失败: {e}")
        return False
    finally:
        if 'storage' in locals():
            storage.close()


def test_integration_with_collectors():
    """测试与数据收集器的集成"""
    print("🔗 测试与数据收集器集成...")

    try:
        storage = StockInfoStorage()

        # 尝试使用Tushare收集器获取真实数据
        print("  📡 尝试从Tushare获取股票信息...")
        try:
            TushareCollector = get_tushare_collector()
            collector = TushareCollector()

            # 获取股票信息（这可能会因为token问题失败）
            stock_info = collector.get_stock_info("000001.SZ")

            if stock_info:
                print(f"  ✅ 从Tushare获取成功: {stock_info.name}")

                # 保存到数据库
                save_success = storage.save_stock_info(stock_info)
                if save_success:
                    print("  ✅ 保存到数据库成功")
                else:
                    print("  ❌ 保存到数据库失败")
            else:
                print("  ⚠️  从Tushare获取失败（可能缺少token）")

        except Exception as e:
            print(f"  ⚠️  Tushare集成测试失败: {e}")

        # 尝试使用AKShare收集器
        print("  📡 尝试从AKShare获取股票信息...")
        try:
            AKShareCollector = get_akshare_collector()
            collector = AKShareCollector()

            # 这里只测试代码规范化，不实际获取数据以避免网络问题
            normalized = collector._normalize_symbol("000001")
            print(f"  ✅ AKShare代码规范化: 000001 -> {normalized}")

        except Exception as e:
            print(f"  ⚠️  AKShare集成测试失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False
    finally:
        if 'storage' in locals():
            storage.close()


def test_file_backup():
    """测试文件备份功能"""
    print("💾 测试文件备份功能...")

    try:
        storage = StockInfoStorage()

        # 创建测试股票
        test_stock = StockInfo(
            symbol="TEST001.SZ", name="测试股票", exchange="SZSE", market="测试板", currency="CNY"
        )

        # 保存并备份
        success = storage.save_stock_info(test_stock, backup=True)

        if success:
            # 检查备份文件是否存在
            backup_file = Path("data/raw/stocks/TEST001.SZ.json")
            if backup_file.exists():
                print("  ✅ 备份文件创建成功")

                # 读取备份文件验证内容
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)

                if backup_data['symbol'] == test_stock.symbol:
                    print("  ✅ 备份内容验证成功")
                else:
                    print("  ❌ 备份内容验证失败")
                    return False
            else:
                print("  ❌ 备份文件未创建")
                return False
        else:
            print("  ❌ 保存失败")
            return False

        return True

    except Exception as e:
        print(f"❌ 文件备份测试失败: {e}")
        return False
    finally:
        if 'storage' in locals():
            storage.close()


def cleanup_test_data():
    """清理测试数据"""
    print("🧹 清理测试数据...")

    try:
        storage = StockInfoStorage()

        # 删除测试股票
        test_symbols = ["000001.SZ", "000002.SZ", "600000.SS", "300001.SZ", "TEST001.SZ"]

        for symbol in test_symbols:
            try:
                storage.delete_stock(symbol)
            except Exception as e:
                print(f"  ⚠️  删除 {symbol} 失败: {e}")

        # 删除备份文件
        backup_dir = Path("data/raw/stocks")
        if backup_dir.exists():
            for file in backup_dir.glob("*.json"):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"  ⚠️  删除备份文件 {file} 失败: {e}")

        print("✅ 测试数据清理完成")

    except Exception as e:
        print(f"❌ 清理测试数据失败: {e}")
    finally:
        if 'storage' in locals():
            storage.close()


def main():
    """主测试函数"""
    logger = get_database_logger()
    logger.info("🚀 开始股票信息存储测试")

    print("=" * 60)
    print("MarketSeer 股票信息存储功能测试")
    print("=" * 60)

    tests = [
        ("数据库连接测试", test_database_connection),
        ("创建股票表测试", test_create_table),
        ("股票存储基本功能测试", test_stock_storage_basic),
        ("批量操作测试", test_batch_operations),
        ("数据收集器集成测试", test_integration_with_collectors),
        ("文件备份功能测试", test_file_backup),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                failed += 1
                print(f"❌ {test_name} 失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 异常: {e}")

    # 清理测试数据
    print(f"\n{'='*60}")
    cleanup_test_data()

    # 测试总结
    print(f"\n{'='*60}")
    print("测试总结")
    print("=" * 60)
    print(f"✅ 通过: {passed} 项")
    print(f"❌ 失败: {failed} 项")
    print(f"📊 总计: {passed + failed} 项")

    if failed == 0:
        print("🎉 所有测试通过！股票信息存储功能完全可用！")
    else:
        print("⚠️  部分测试失败，请检查配置和数据库连接！")

    logger.info("测试完成")


if __name__ == "__main__":
    import json  # 添加json导入

    main()
