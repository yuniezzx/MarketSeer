"""
临时快速建表脚本

用法:
    python scripts/init_db.py

说明:
- 使用 models.base.Base 来创建表（确保与模型定义使用相同的 Base）。
- 使用 config.database.engine 作为绑定引擎。
- 该脚本在本地开发/测试环境下快速创建表。生产请使用 Alembic 等迁移工具。
"""

import os
import sys

# Ensure project root is on sys.path so package imports work when running the script directly.
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config.database import engine
from models.base import Base


def main() -> int:
    try:
        print("使用 engine:", engine)
        print("正在创建表...")
        Base.metadata.create_all(bind=engine)
        print("表创建完成（若已存在则保持不变）。")
        return 0
    except Exception as e:
        print("创建表时出错:", e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
