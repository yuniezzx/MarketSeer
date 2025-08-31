"""
数据库连接测试脚本

用于测试数据库连接是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from config.database import DatabaseConfig, create_database_engine


def test_database_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("MarketSeer 数据库连接测试")
    print("=" * 50)

    # 加载环境变量
    load_dotenv()

    # 显示当前配置
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    print(f"数据库类型: {db_type}")

    if db_type == "mysql":
        print(f"MySQL主机: {DatabaseConfig.DB_HOST}")
        print(f"MySQL端口: {DatabaseConfig.DB_PORT}")
        print(f"MySQL用户: {DatabaseConfig.DB_USER}")
        print(f"MySQL数据库: {DatabaseConfig.DB_NAME}")
    elif db_type == "postgresql":
        print(f"PostgreSQL主机: {DatabaseConfig.DB_HOST}")
        print(f"PostgreSQL端口: {DatabaseConfig.DB_PORT}")
        print(f"PostgreSQL用户: {DatabaseConfig.DB_USER}")
        print(f"PostgreSQL数据库: {DatabaseConfig.DB_NAME}")
    else:
        print(f"SQLite路径: {DatabaseConfig.SQLITE_PATH}")

    print("-" * 30)
    print("开始连接测试...")

    try:
        # 创建数据库引擎
        engine = create_database_engine()
        print("✓ 数据库引擎创建成功")

        # 测试连接
        with engine.connect() as connection:
            print("✓ 数据库连接建立成功")

            # 执行简单查询测试
            if db_type == "mysql":
                result = connection.execute(text("SELECT VERSION() as version"))
                version = result.fetchone()
                print(f"✓ MySQL版本: {version[0]}")

                # 测试数据库是否存在
                result = connection.execute(text("SELECT DATABASE() as db_name"))
                db_name = result.fetchone()
                print(f"✓ 当前数据库: {db_name[0]}")

            elif db_type == "postgresql":
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()
                print(f"✓ PostgreSQL版本: {version[0]}")

                result = connection.execute(text("SELECT current_database()"))
                db_name = result.fetchone()
                print(f"✓ 当前数据库: {db_name[0]}")

            else:  # SQLite
                result = connection.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()
                print(f"✓ SQLite版本: {version[0]}")

                # 检查SQLite文件路径
                sqlite_path = Path(DatabaseConfig.SQLITE_PATH)
                if sqlite_path.exists():
                    print(f"✓ SQLite文件存在: {sqlite_path.absolute()}")
                else:
                    print(f"! SQLite文件将被创建: {sqlite_path.absolute()}")

            print("✓ 数据库查询测试成功")

        print("-" * 30)
        print("🎉 数据库连接测试完全成功!")
        return True

    except SQLAlchemyError as e:
        print("❌ 数据库连接失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        print("-" * 30)
        print("请检查以下配置:")
        print("1. 数据库服务是否启动")
        print("2. 连接参数是否正确")
        print("3. 用户权限是否足够")
        print("4. 网络连接是否正常")
        return False

    except Exception as e:
        print("❌ 发生未知错误!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        return False


def test_environment_variables():
    """测试环境变量配置"""
    print("\n" + "=" * 50)
    print("环境变量配置检查")
    print("=" * 50)

    required_vars = []
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "mysql":
        required_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    elif db_type == "postgresql":
        required_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    else:
        required_vars = ["SQLITE_PATH"]

    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隐藏密码显示
            if "PASSWORD" in var:
                print(f"✓ {var}: {'*' * len(value)}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"❌ {var}: 未设置")
            all_ok = False

    if all_ok:
        print("✓ 所有必需环境变量已设置")
    else:
        print("❌ 存在未设置的环境变量")

    return all_ok


def main():
    """主函数"""
    print("开始MarketSeer数据库测试...\n")

    # 测试环境变量
    env_ok = test_environment_variables()

    if not env_ok:
        print("\n环境变量配置有问题，请先检查.env文件")
        return

    # 测试数据库连接
    db_ok = test_database_connection()

    print("\n" + "=" * 50)
    if db_ok:
        print("🎉 所有测试通过! 数据库配置正确!")
    else:
        print("❌ 测试失败! 请检查数据库配置!")
    print("=" * 50)


if __name__ == "__main__":
    main()
