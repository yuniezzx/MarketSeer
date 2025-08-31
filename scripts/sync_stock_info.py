"""
批量同步选中股票基本信息到 stock_info 表的脚本

用法示例:
  # 单个或多个代码参数
  python scripts/sync_stock_info.py --codes 600519 000002

  # 从文件读取（每行一个代码）
  python scripts/sync_stock_info.py --file data/codes.txt

说明:
- 使用纯数字代码列表（例如 "600519"），脚本会调用 data.StockInfoAggregator.aggregate_and_upsert_many 并写入 DB。
- 不记录字段来源（按你的要求）。
"""

import os
import sys

_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

import argparse
from config.database import SessionLocal
from data.stock_info_aggregator import StockInfoAggregator


def load_codes_from_file(path: str):
    codes = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                codes.append(s)
    return codes


def main():
    p = argparse.ArgumentParser(description="Sync stock basic info to DB (stock_info)")
    p.add_argument("--codes", nargs="+", help="List of stock codes (e.g. 600519 000002)")
    p.add_argument("--file", help="Path to file with one code per line")
    p.add_argument("--chunk-size", type=int, default=50, help="Commit chunk size")
    args = p.parse_args()

    codes = []
    if args.codes:
        codes.extend(args.codes)
    if args.file:
        codes_from_file = load_codes_from_file(args.file)
        codes.extend(codes_from_file)

    if not codes:
        print("未提供任何股票代码。使用 --codes 或 --file 指定。")
        return 2

    agg = StockInfoAggregator()
    session = SessionLocal()
    try:
        summary = agg.aggregate_and_upsert_many(codes, session=session, chunk_size=args.chunk_size)
        print("同步完成：")
        print(f"  total: {summary['total']}")
        print(f"  succeeded: {summary['succeeded']}")
        print(f"  failed: {summary['failed']}")
        # 简短输出失败条目
        for r in summary["results"]:
            if r.get("error"):
                print(f"  FAIL {r.get('code')}: {r.get('error')}")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
