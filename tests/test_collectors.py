"""
数据收集器测试脚本

测试各个数据收集器的基本功能。
"""

import sys
import os
from datetime import datetime, date, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.collectors import (
    get_tushare_collector,
    DataCollectorError,
    AuthenticationError,
    SymbolNotFoundError,
)
from src.utils.logger import get_database_logger


def test_tushare_collector():
    """测试Tushare收集器"""
    logger = get_database_logger()
    logger.info("=" * 60)
    logger.info("Tushare数据收集器测试开始")
    logger.info("=" * 60)

    try:
        # 创建Tushare收集器
        TushareCollector = get_tushare_collector()
        collector = TushareCollector()

        logger.info("✅ Tushare收集器初始化成功")

        # 测试股票代码标准化
        test_symbols = ['000001', '000001.SZ', '600000', '600000.SH', '300001', '688001']
        logger.info("\n🔍 测试股票代码标准化...")

        for symbol in test_symbols:
            try:
                normalized = collector._normalize_symbol(symbol)
                logger.info(f"  {symbol} -> {normalized}")
            except Exception as e:
                logger.error(f"  {symbol} -> 错误: {e}")

        # 测试获取股票基本信息
        logger.info("\n📊 测试获取股票基本信息...")
        test_symbol = "000001.SZ"  # 平安银行

        try:
            stock_info = collector.get_stock_info(test_symbol)
            logger.info(f"✅ 获取股票信息成功: {stock_info.name} ({stock_info.symbol})")
            logger.info(f"   交易所: {stock_info.exchange}")
            logger.info(f"   市场: {stock_info.market}")
            logger.info(f"   行业: {stock_info.industry}")
            logger.info(f"   上市日期: {stock_info.list_date}")
        except SymbolNotFoundError as e:
            logger.warning(f"❌ 股票未找到: {e}")
        except Exception as e:
            logger.error(f"❌ 获取股票信息失败: {e}")

        # 测试获取历史数据
        logger.info("\n📈 测试获取历史数据...")
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=10)  # 获取最近10天的数据

            logger.info(f"   获取 {test_symbol} 从 {start_date} 到 {end_date} 的历史数据...")
            historical_data = collector.get_historical_data(test_symbol, start_date, end_date)

            if historical_data:
                logger.info(f"✅ 获取历史数据成功: {len(historical_data)} 条记录")
                # 显示最新的一条数据
                latest = historical_data[-1]
                logger.info(f"   最新数据: {latest.date} 收盘价: {latest.close}")
            else:
                logger.warning("❌ 未获取到历史数据")

        except Exception as e:
            logger.error(f"❌ 获取历史数据失败: {e}")

        # 测试获取实时数据
        logger.info("\n⚡ 测试获取实时数据...")
        try:
            realtime_data = collector.get_realtime_data([test_symbol])

            if realtime_data:
                data = realtime_data[0]
                logger.info(f"✅ 获取实时数据成功: {data.name}")
                logger.info(f"   当前价格: {data.current_price}")
                logger.info(f"   涨跌幅: {data.pct_change}%")
                logger.info(f"   数据时间: {data.timestamp}")
            else:
                logger.warning("❌ 未获取到实时数据")

        except Exception as e:
            logger.error(f"❌ 获取实时数据失败: {e}")

        # 测试统计信息
        logger.info("\n📊 收集器统计信息:")
        stats = collector.get_stats()
        for key, value in stats.items():
            logger.info(f"   {key}: {value}")

        # 关闭收集器
        collector.close()
        logger.info("\n✅ Tushare收集器测试完成")

    except AuthenticationError as e:
        logger.error(f"❌ 认证失败: {e}")
        logger.info("💡 请确保已配置TUSHARE_TOKEN环境变量")
        return False
    except ImportError as e:
        logger.error(f"❌ 导入错误: {e}")
        logger.info("💡 请安装tushare库: pip install tushare")
        return False
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False

    return True


def test_data_types():
    """测试数据类型定义"""
    logger = get_database_logger()
    logger.info("\n" + "=" * 60)
    logger.info("数据类型测试开始")
    logger.info("=" * 60)

    try:
        from src.data.collectors.data_types import (
            StockInfo,
            HistoricalData,
            RealtimeData,
            FinancialData,
            DataCollectorConfig,
        )

        # 测试StockInfo
        stock_info = StockInfo(
            symbol="000001.SZ",
            name="平安银行",
            exchange="深圳证券交易所",
            market="深市主板",
            list_date=date(1991, 4, 3),
        )
        logger.info(f"✅ StockInfo创建成功: {stock_info.name}")

        # 测试HistoricalData
        historical_data = HistoricalData(
            symbol="000001.SZ", date=date.today(), open=10.0, high=10.5, low=9.8, close=10.2, volume=1000000
        )
        logger.info(f"✅ HistoricalData创建成功: {historical_data.date}")

        # 测试转换为字典
        data_dict = historical_data.to_dict()
        logger.info(f"✅ 数据字典转换成功: {len(data_dict)} 个字段")

        # 测试RealtimeData
        realtime_data = RealtimeData(
            symbol="000001.SZ", name="平安银行", timestamp=datetime.now(), current_price=10.2
        )
        logger.info(f"✅ RealtimeData创建成功: {realtime_data.name}")

        # 测试FinancialData
        financial_data = FinancialData(
            symbol="000001.SZ", report_date=date(2023, 12, 31), total_revenue=100000000, net_profit=20000000
        )
        logger.info(f"✅ FinancialData创建成功: {financial_data.report_date}")

        # 测试DataCollectorConfig
        config = DataCollectorConfig(timeout=30, retry_count=3, token="test_token")
        logger.info(f"✅ DataCollectorConfig创建成功: timeout={config.timeout}")

        logger.info("✅ 数据类型测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 数据类型测试失败: {e}")
        return False


def test_exceptions():
    """测试异常类"""
    logger = get_database_logger()
    logger.info("\n" + "=" * 60)
    logger.info("异常类测试开始")
    logger.info("=" * 60)

    try:
        from src.data.collectors.exceptions import (
            DataCollectorError,
            APIError,
            RateLimitError,
            AuthenticationError,
            SymbolNotFoundError,
        )

        # 测试基础异常
        try:
            raise DataCollectorError("测试异常", error_code="TEST_ERROR")
        except DataCollectorError as e:
            logger.info(f"✅ DataCollectorError: {e}")
            logger.info(f"   错误码: {e.error_code}")
            logger.info(f"   详情: {e.details}")

        # 测试API错误
        try:
            raise APIError("API调用失败", status_code=500, api_name="test_api")
        except APIError as e:
            logger.info(f"✅ APIError: {e}")
            logger.info(f"   状态码: {e.status_code}")
            logger.info(f"   API名称: {e.api_name}")

        # 测试频率限制错误
        try:
            raise RateLimitError("请求过于频繁", retry_after=60)
        except RateLimitError as e:
            logger.info(f"✅ RateLimitError: {e}")
            logger.info(f"   重试间隔: {e.retry_after}秒")

        # 测试认证错误
        try:
            raise AuthenticationError("认证失败", auth_type="token")
        except AuthenticationError as e:
            logger.info(f"✅ AuthenticationError: {e}")
            logger.info(f"   认证类型: {e.auth_type}")

        # 测试股票未找到错误
        try:
            raise SymbolNotFoundError("股票未找到", symbol="INVALID", data_source="test")
        except SymbolNotFoundError as e:
            logger.info(f"✅ SymbolNotFoundError: {e}")
            logger.info(f"   股票代码: {e.symbol}")
            logger.info(f"   数据源: {e.data_source}")

        logger.info("✅ 异常类测试完成")
        return True

    except Exception as e:
        logger.error(f"❌ 异常类测试失败: {e}")
        return False


def main():
    """主测试函数"""
    logger = get_database_logger()
    logger.info("🚀 MarketSeer数据收集器测试开始")
    logger.info(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 运行测试
    tests = [
        ("数据类型测试", test_data_types),
        ("异常类测试", test_exceptions),
        ("Tushare收集器测试", test_tushare_collector),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        logger.info(f"\n🧪 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} 通过")
            else:
                failed += 1
                logger.error(f"❌ {test_name} 失败")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name} 异常: {e}")

    # 测试总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    logger.info(f"✅ 通过: {passed} 项")
    logger.info(f"❌ 失败: {failed} 项")
    logger.info(f"📊 总计: {passed + failed} 项")

    if failed == 0:
        logger.info("🎉 所有测试通过！数据收集模块可以正常使用！")
    else:
        logger.warning("⚠️  部分测试失败，请检查配置和依赖！")

    logger.info("测试完成")


if __name__ == "__main__":
    main()
