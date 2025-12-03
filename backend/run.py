"""
MarketSeer 后端启动脚本
"""

import os
import argparse
from dotenv import load_dotenv
from app import create_app
from app.models import db
from pathlib import Path
from logger import logger
from config import Config

# 加载 .env 文件
load_dotenv()


def get_database_uri(db_type):
    """根据数据库类型获取连接 URI"""
    if db_type == 'sqlite':
        # 使用默认的 SQLite 数据库
        base_dir = Path(__file__).parent
        data_dir = base_dir / 'data'
        # 确保 data 目录存在
        data_dir.mkdir(parents=True, exist_ok=True)
        return f'sqlite:///{data_dir / "marketseer.db"}'
    elif db_type == 'supabase':
        # 从环境变量读取 Supabase 配置
        supabase_uri = os.environ.get('SUPABASE_DATABASE_URI')
        if not supabase_uri:
            raise ValueError(
                "使用 Supabase 数据库需要在 .env 文件中配置 SUPABASE_DATABASE_URI\n"
                "格式: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
            )
        return supabase_uri
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")


# 解析命令行参数
parser = argparse.ArgumentParser(description='MarketSeer 后端服务')
parser.add_argument(
    '--db', type=str, choices=['sqlite', 'supabase'], default='sqlite', help='数据库类型 (默认: sqlite)'
)
args = parser.parse_args()

# 获取数据库 URI
database_uri = get_database_uri(args.db)

# 设置数据库 URI 到环境变量 (这样 config.py 就能读取到)
os.environ['SQLALCHEMY_DATABASE_URI'] = database_uri

# 创建 Flask 应用
app = create_app()


if __name__ == '__main__':
    # 获取环境变量配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    logger.info("=" * 60)
    logger.info("MarketSeer 后端服务启动中...")
    logger.info(f"数据库类型: {args.db}")
    logger.info(f"Debug: {debug}")
    logger.info(f"API Base URL: http://{host}:{port}/api")
    logger.info("=" * 60)

    try:
        app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
    except KeyboardInterrupt:
        logger.warning("收到停止信号，正在关闭服务...")
    except Exception as e:
        logger.exception(f"服务启动失败: {e}")
    finally:
        logger.info("MarketSeer 后端服务已停止")
