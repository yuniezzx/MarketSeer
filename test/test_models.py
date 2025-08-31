"""
数据模型测试脚本

测试数据模型的创建和基本功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, date
from decimal import Decimal
from config.database import create_database_engine, Base
from models import StockInfo, StockPrice, Stock, Market, Index, Sector


def test_create_tables():
    """测试创建数据表"""
    print("=" * 50)
    print("数据模型表结构测试")
    print("=" * 50)

    try:
        # 创建数据库引擎
        engine = create_database_engine()
        print("✓ 数据库引擎创建成功")

        # 创建所有表
        Base.metadata.create_all(engine)
        print("✓ 数据库表创建成功")

        # 显示创建的表
        inspector = engine.inspect(engine)
        tables = inspector.get_table_names()
        print(f"✓ 创建的表数量: {len(tables)}")
        for table in tables:
            print(f"  - {table}")

        return True

    except Exception as e:
        print("❌ 创建表失败!")
        print(f"错误: {str(e)}")
        return False


def test_stock_info_model():
    """测试股票基本信息模型"""
    print("\n" + "-" * 30)
    print("测试 StockInfo 模型")
    print("-" * 30)

    try:
        # 创建股票信息实例
        stock_info = StockInfo(
            symbol="000001.SZ",
            code="000001",
            market="SZ",
            name="平安银行",
            full_name="平安银行股份有限公司",
            industry="银行",
            sector="金融业",
            company_type="股份有限公司",
            registered_capital=Decimal("1945617.34"),
            listing_date=date(1991, 4, 3),
            province="广东省",
            city="深圳市",
            total_shares=19405918198,
            circulating_shares=19405918198,
            pe_ratio=Decimal("4.52"),
            pb_ratio=Decimal("0.58"),
            status="正常",
            is_st=False,
            currency="CNY",
            lot_size=100,
        )

        print("✓ StockInfo 实例创建成功")
        print(f"  股票代码: {stock_info.symbol}")
        print(f"  股票名称: {stock_info.name}")
        print(f"  所属市场: {stock_info.market}")
        print(f"  所属行业: {stock_info.industry}")

        # 测试 to_dict 方法
        stock_dict = stock_info.to_dict()
        print(f"✓ to_dict 方法测试成功，字段数: {len(stock_dict)}")

        return True

    except Exception as e:
        print("❌ StockInfo 模型测试失败!")
        print(f"错误: {str(e)}")
        return False


def test_stock_price_model():
    """测试股票价格模型"""
    print("\n" + "-" * 30)
    print("测试 StockPrice 模型")
    print("-" * 30)

    try:
        # 创建股票价格实例
        stock_price = StockPrice(
            symbol="000001.SZ",
            trade_date=date(2024, 8, 31),
            open_price=Decimal("10.50"),
            high_price=Decimal("10.80"),
            low_price=Decimal("10.30"),
            close_price=Decimal("10.65"),
            pre_close=Decimal("10.45"),
            volume=50000000,
            amount=Decimal("530000000.00"),
            change=Decimal("0.20"),
            pct_change=Decimal("1.91"),
            turnover_rate=Decimal("2.58"),
        )

        print("✓ StockPrice 实例创建成功")
        print(f"  股票代码: {stock_price.symbol}")
        print(f"  交易日期: {stock_price.trade_date}")
        print(f"  收盘价: {stock_price.close_price}")
        print(f"  涨跌幅: {stock_price.pct_change}%")

        return True

    except Exception as e:
        print("❌ StockPrice 模型测试失败!")
        print(f"错误: {str(e)}")
        return False


def test_market_model():
    """测试市场模型"""
    print("\n" + "-" * 30)
    print("测试 Market 模型")
    print("-" * 30)

    try:
        # 创建市场实例
        market = Market(
            code="SZ",
            name="深圳证券交易所",
            full_name="深圳证券交易所",
            country="CN",
            currency="CNY",
            timezone="Asia/Shanghai",
            trading_start="09:30",
            trading_end="15:00",
            lunch_break_start="11:30",
            lunch_break_end="13:00",
        )

        print("✓ Market 实例创建成功")
        print(f"  市场代码: {market.code}")
        print(f"  市场名称: {market.name}")
        print(f"  交易时间: {market.trading_start} - {market.trading_end}")

        return True

    except Exception as e:
        print("❌ Market 模型测试失败!")
        print(f"错误: {str(e)}")
        return False


def test_index_model():
    """测试指数模型"""
    print("\n" + "-" * 30)
    print("测试 Index 模型")
    print("-" * 30)

    try:
        # 创建指数实例
        index = Index(
            code="000001.SH",
            name="上证指数",
            full_name="上海证券交易所综合股价指数",
            market="SH",
            category="综合指数",
            base_date=date(1990, 12, 19),
            base_point=Decimal("100.00"),
            weight_method="市值加权",
            constituent_count=1000,
            publisher="上海证券交易所",
            publish_date=date(1991, 7, 15),
        )

        print("✓ Index 实例创建成功")
        print(f"  指数代码: {index.code}")
        print(f"  指数名称: {index.name}")
        print(f"  基准点数: {index.base_point}")
        print(f"  成分股数: {index.constituent_count}")

        return True

    except Exception as e:
        print("❌ Index 模型测试失败!")
        print(f"错误: {str(e)}")
        return False


def test_sector_model():
    """测试板块模型"""
    print("\n" + "-" * 30)
    print("测试 Sector 模型")
    print("-" * 30)

    try:
        # 创建板块实例
        sector = Sector(
            code="BK0001",
            name="银行",
            category="行业板块",
            level=1,
            stock_count=42,
            total_market_cap=Decimal("15000000000000.00"),
            avg_pe_ratio=Decimal("5.2"),
        )

        print("✓ Sector 实例创建成功")
        print(f"  板块代码: {sector.code}")
        print(f"  板块名称: {sector.name}")
        print(f"  板块类别: {sector.category}")
        print(f"  股票数量: {sector.stock_count}")

        return True

    except Exception as e:
        print("❌ Sector 模型测试失败!")
        print(f"错误: {str(e)}")
        return False


def main():
    """主函数"""
    print("开始MarketSeer数据模型测试...\n")

    results = []

    # 测试创建表
    results.append(test_create_tables())

    # 测试各个模型
    results.append(test_stock_info_model())
    results.append(test_stock_price_model())
    results.append(test_market_model())
    results.append(test_index_model())
    results.append(test_sector_model())

    # 统计结果
    success_count = sum(results)
    total_count = len(results)

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")

    if success_count == total_count:
        print("🎉 所有测试通过! 数据模型创建成功!")
    else:
        print("❌ 部分测试失败! 请检查错误信息!")

    print("=" * 50)


if __name__ == "__main__":
    main()
