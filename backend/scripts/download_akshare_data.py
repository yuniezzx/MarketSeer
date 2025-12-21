"""
通用 akshare 数据下载脚本

用于下载指定 akshare API 的数据并保存到本地文件

使用示例：
    # 下载活跃营业部数据
    python scripts/download_akshare_data.py --api stock_lhb_hyyyb_em --start-date 20251218 --end-date 20251218

    # 下载指定日期范围的数据
    python scripts/download_akshare_data.py --api stock_lhb_hyyyb_em --start-date 20251215 --end-date 20251219
"""

import sys
import argparse
import pandas as pd
import json
from datetime import datetime, timedelta, date
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.data_sources.akshare_client import AkshareClient
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


def download_single_date(client: AkshareClient, api_name: str, date: str) -> bool:
    """
    下载单个日期的数据

    Args:
        client: akshare 客户端实例
        api_name: API 名称
        date: 日期 (YYYYMMDD)

    Returns:
        是否成功
    """
    logger.info("=" * 60)
    logger.info(f"下载 API: {api_name}, 日期: {date}")
    logger.info("=" * 60)

    try:
        # 调用 API
        params = {"start_date": date, "end_date": date}

        data = client.fetch(api_name, params)

        if data is None:
            logger.error(f"✗ API 返回空数据: {api_name}")
            return False

        # 确保数据是 DataFrame
        if not isinstance(data, pd.DataFrame):
            logger.error(f"✗ API 返回数据类型不支持: {type(data)}")
            return False

        # 保存到 data/akshare_raw 目录
        data_dir = backend_dir / "data" / "akshare_raw"
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{api_name}_{date}_{date}.json"
        filepath = data_dir / filename

        # 转换为字典列表格式，处理日期类型
        data_records = data.to_dict(orient="records")

        # 将日期对象转换为字符串
        for record in data_records:
            for key, value in record.items():
                if hasattr(value, "isoformat"):  # 检查是否有日期方法
                    record[key] = str(value)
                elif pd.isna(value):  # 处理NaN值
                    record[key] = None

        data_dict = {
            "api_name": api_name,
            "params": params,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "data": data_records,
        }

        # 保存为 JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ 数据已保存到: {filepath}")
        logger.info(f"✓ 数据行数: {len(data)}")
        logger.info(f"✓ 数据列数: {len(data.columns)}")

        return True

    except Exception as e:
        logger.error(f"✗ 下载失败: {str(e)}")
        return False


def download_date_range(
    client: AkshareClient, api_name: str, start_date: str, end_date: str
) -> tuple[int, int]:
    """
    下载日期范围的数据

    Args:
        client: akshare 客户端实例
        api_name: API 名称
        start_date: 开始日期 (YYYYMMDD)
        end_date: 结束日期 (YYYYMMDD)

    Returns:
        (成功次数, 失败次数)
    """
    dates = generate_date_range(start_date, end_date)

    success_count = 0
    failed_count = 0

    logger.info("=" * 60)
    logger.info(f"开始批量下载 {api_name} 数据")
    logger.info(f"日期范围: {start_date} - {end_date}")
    logger.info(f"日期数量: {len(dates)}")
    logger.info("=" * 60)

    for date in dates:
        if download_single_date(client, api_name, date):
            success_count += 1
        else:
            failed_count += 1

    return success_count, failed_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="通用 akshare 数据下载脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 下载单日数据
  python scripts/download_akshare_data.py --api stock_lhb_hyyyb_em --start-date 20251218 --end-date 20251218

  # 下载日期范围数据
  python scripts/download_akshare_data.py --api stock_lhb_hyyyb_em --start-date 20251215 --end-date 20251219
        """,
    )

    parser.add_argument("--api", type=str, required=True, help="akshare API 名称")

    parser.add_argument("--start-date", type=str, required=True, help="开始日期 (格式: YYYYMMDD)")

    parser.add_argument("--end-date", type=str, required=True, help="结束日期 (格式: YYYYMMDD)")

    args = parser.parse_args()

    # 参数验证
    if not validate_date(args.start_date):
        logger.error(f"错误: 无效的开始日期格式: {args.start_date}")
        sys.exit(1)

    if not validate_date(args.end_date):
        logger.error(f"错误: 无效的结束日期格式: {args.end_date}")
        sys.exit(1)

    if args.start_date > args.end_date:
        logger.error("错误: 开始日期不能晚于结束日期")
        sys.exit(1)

    # 创建客户端实例
    client = AkshareClient()

    # 下载数据
    success_count, failed_count = download_date_range(
        client, args.api, args.start_date, args.end_date
    )

    # 输出总结
    logger.info("=" * 60)
    logger.info("下载完成")
    logger.info(f"成功: {success_count} 天")
    logger.info(f"失败: {failed_count} 天")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
