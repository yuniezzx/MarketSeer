"""
测试运行器

提供便捷的测试执行入口
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import argparse
from test_database_connection import main as test_db_main


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MarketSeer 测试运行器")
    parser.add_argument(
        '--test', type=str, choices=['db', 'database', 'all'], default='all', help='选择要运行的测试'
    )

    args = parser.parse_args()

    print("MarketSeer 测试运行器")
    print("=" * 30)

    if args.test in ['db', 'database', 'all']:
        print("运行数据库连接测试...")
        test_db_main()

    if args.test == 'all':
        print("\n所有测试执行完成!")


if __name__ == "__main__":
    main()
