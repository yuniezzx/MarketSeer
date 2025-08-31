"""
数据库连接测试脚本

用于测试MySQL数据库连接和基本功能。
"""

import os
import sys
from datetime import datetime
import pandas as pd

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.data.storage.database import get_database, close_database


def test_database_connection():
    """测试数据库连接"""
    logger = get_logger("test_database")

    try:
        # 获取数据库实例
        db = get_database()
        logger.info("数据库连接测试开始")

        # 测试基本查询
        logger.info("执行基本查询测试...")
        result = db.execute_query("SELECT 1 as test_value, NOW() as current_time")
        logger.info(f"查询结果: {result}")

        # 获取数据库连接信息
        logger.info("获取数据库连接信息...")
        conn_info = db.get_connection_info()
        logger.info(f"连接信息: {conn_info}")

        # 测试DataFrame操作
        logger.info("测试DataFrame查询...")
        df = db.read_dataframe("SELECT 1 as id, 'test' as name, NOW() as created_at")
        logger.info(f"DataFrame结果:\n{df}")

        return True

    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False


def test_table_operations():
    """测试表操作"""
    logger = get_logger("test_table")

    try:
        db = get_database()
        test_table = "test_marketseer"

        # 删除测试表（如果存在）
        if db.table_exists(test_table):
            logger.info(f"删除已存在的测试表: {test_table}")
            db.execute_command(f"DROP TABLE IF EXISTS {test_table}")

        # 创建测试表
        logger.info(f"创建测试表: {test_table}")
        table_columns = {
            'id': 'primary_key',
            'symbol': 'string',
            'price': 'float',
            'volume': 'integer',
            'created_at': 'datetime',
        }
        db.create_table(test_table, table_columns)

        # 检查表是否存在
        if db.table_exists(test_table):
            logger.info(f"表 {test_table} 创建成功")
        else:
            logger.error(f"表 {test_table} 创建失败")
            return False

        # 获取表信息
        table_info = db.get_table_info(test_table)
        logger.info(f"表信息: {table_info}")

        # 插入测试数据
        logger.info("插入测试数据...")
        test_data = [
            {'symbol': '000001.SZ', 'price': 10.50, 'volume': 1000},
            {'symbol': '000002.SZ', 'price': 15.30, 'volume': 2000},
            {'symbol': '600000.SH', 'price': 8.90, 'volume': 1500},
        ]

        for data in test_data:
            db.execute_command(
                f"INSERT INTO {test_table} (symbol, price, volume, created_at) VALUES (:symbol, :price, :volume, NOW())",
                data,
            )

        # 查询数据
        logger.info("查询插入的数据...")
        results = db.execute_query(f"SELECT * FROM {test_table}")
        logger.info(f"查询结果: {results}")

        # 使用DataFrame保存数据
        logger.info("测试DataFrame保存...")
        df_test = pd.DataFrame(
            [
                {'symbol': '300001.SZ', 'price': 25.60, 'volume': 3000, 'created_at': datetime.now()},
                {'symbol': '300002.SZ', 'price': 18.40, 'volume': 2500, 'created_at': datetime.now()},
            ]
        )

        db.save_dataframe(df_test, test_table, if_exists='append', index=False)

        # 查询所有数据
        logger.info("查询所有数据...")
        all_data = db.read_dataframe(f"SELECT * FROM {test_table} ORDER BY id")
        logger.info(f"所有数据:\n{all_data}")

        # 清理测试表
        logger.info(f"清理测试表: {test_table}")
        db.execute_command(f"DROP TABLE {test_table}")

        return True

    except Exception as e:
        logger.error(f"表操作测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    logger = get_logger("main")
    logger.info("=" * 50)
    logger.info("MarketSeer 数据库连接测试开始")
    logger.info("=" * 50)

    # 检查配置
    config = get_config()
    logger.info("检查配置文件...")

    try:
        db_config = config.get_database_config()
        logger.info(f"数据库配置: {db_config}")

        if not db_config:
            logger.error("未找到数据库配置，请检查 config/config.yaml 文件")
            return False

    except Exception as e:
        logger.error(f"配置文件加载失败: {str(e)}")
        return False

    # 测试数据库连接
    logger.info("\n1. 测试数据库连接...")
    if not test_database_connection():
        logger.error("数据库连接测试失败")
        return False

    # 测试表操作
    logger.info("\n2. 测试表操作...")
    if not test_table_operations():
        logger.error("表操作测试失败")
        return False

    logger.info("\n" + "=" * 50)
    logger.info("所有测试通过！数据库配置成功！")
    logger.info("=" * 50)

    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 数据库测试成功！")
            print("🎉 MySQL连接配置完成，可以开始使用数据库功能了！")
        else:
            print("\n❌ 数据库测试失败！")
            print("💡 请检查以下配置：")
            print("   1. MySQL服务是否启动")
            print("   2. config/.env 文件中的数据库密码是否正确")
            print("   3. config/config.yaml 中的数据库配置是否正确")
            print("   4. 数据库 'marketseer' 是否存在")
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
    finally:
        # 清理数据库连接
        close_database()
        print("数据库连接已关闭")
