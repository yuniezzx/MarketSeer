"""
活跃营业部数据导入脚本

用于将指定日期的活跃营业部数据导入数据库

使用示例：
    # 导入指定日期数据
    python scripts/range_upsert_daily_active_brokerage.py --date 20251219

    # 导入日期范围数据
    python scripts/range_upsert_daily_active_brokerage.py --start-date 20251215 --end-date 20251219
"""

import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.services.active_brokerage_service import ActiveBrokerageService
from logger import logger


def validate_date(date_str: str) -> bool:
    """
    验证日期格式

    Args:
        date_str: 日期字符串 (YYYYMMDD)

    Returns:
        是否有效
    """
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False


def generate_date_range(start_date: str, end_date: str) -> list[str]:
    """
    生成日期范围列表

    Args:
        start_date: 开始日期 (YYYYMMDD)
        end_date: 结束日期 (YYYYMMDD)

    Returns:
        日期列表
    """
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)

    return dates


def import_single_date(service: ActiveBrokerageService, date: str) -> bool:
    """
    导入单个日期的数据

    Args:
        service: 活跃营业部服务实例
        date: 日期 (YYYYMMDD)

    Returns:
        是否成功
    """
    logger.info("=" * 60)
    logger.info(f"导入日期: {date}")
    logger.info("=" * 60)

    success, msg, created, updated = service.import_by_date(date)

    if success:
        logger.info(f"✓ {msg}")
    else:
        logger.error(f"✗ {msg}")

    return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="活跃营业部数据导入脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 导入指定日期数据
  python scripts/range_upsert_daily_active_brokerage.py --date 20251219
  
  # 导入日期范围数据
  python scripts/range_upsert_daily_active_brokerage.py --start-date 20251215 --end-date 20251219
        """,
    )

    parser.add_argument("--date", type=str, help="指定日期 (格式: YYYYMMDD，如 20251219)")

    parser.add_argument("--start-date", type=str, help="开始日期 (格式: YYYYMMDD)")

    parser.add_argument("--end-date", type=str, help="结束日期 (格式: YYYYMMDD)")

    args = parser.parse_args()

    # 参数验证
    if args.date and (args.start_date or args.end_date):
        logger.error("错误: --date 不能与 --start-date/--end-date 同时使用")
        sys.exit(1)

    if not args.date and not (args.start_date and args.end_date):
        logger.error("错误: 请提供 --date 或 --start-date 和 --end-date")
        parser.print_help()
        sys.exit(1)

    # 确定要导入的日期列表
    if args.date:
        if not validate_date(args.date):
            logger.error(f"错误: 无效的日期格式: {args.date}")
            sys.exit(1)
        dates = [args.date]
    else:
        if not validate_date(args.start_date):
            logger.error(f"错误: 无效的开始日期格式: {args.start_date}")
            sys.exit(1)
        if not validate_date(args.end_date):
            logger.error(f"错误: 无效的结束日期格式: {args.end_date}")
            sys.exit(1)
        dates = generate_date_range(args.start_date, args.end_date)

    # 创建 Flask 应用上下文
    app = create_app()

    with app.app_context():
        # 创建服务实例
        service = ActiveBrokerageService()

        # 统计信息
        total_success = 0
        total_failed = 0
        total_created = 0
        total_updated = 0

        logger.info("=" * 60)
        logger.info("开始批量导入活跃营业部数据")
        logger.info(f"日期数量: {len(dates)}")
        logger.info("=" * 60)

        # 逐个导入
        for date in dates:
            success, msg, created, updated = service.import_by_date(date)

            if success:
                total_success += 1
                total_created += created
                total_updated += updated
            else:
                total_failed += 1

        # 输出总结
        logger.info("=" * 60)
        logger.info("导入完成")
        logger.info(f"成功: {total_success} 天")
        logger.info(f"失败: {total_failed} 天")
        logger.info(f"总计创建: {total_created} 条")
        logger.info(f"总计更新: {total_updated} 条")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
