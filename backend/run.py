"""
MarketSeer 后端启动脚本
"""

from app import create_app
from config import Config
from logger import logger


config = Config()

# 创建 Flask 应用
app = create_app()


if __name__ == "__main__":
    # 获取环境变量配置
    env = config.ENV
    host = config.FLASK_HOST
    port = config.FLASK_PORT
    debug = config.FLASK_DEBUG

    logger.info("=" * 60)
    logger.info("MarketSeer Backend Server Starting...")
    logger.info(f"Environment: {'Development' if env == 'development' else 'Production'}")
    logger.info(f"Debug: {debug}")
    logger.info(f"API Base URL: http://{host}:{port}/api")
    logger.info("=" * 60)

    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.warning("Received stop signal, shutting down server...")
    except Exception as e:
        logger.exception(f"Server startup failed: {e}")
    finally:
        logger.info("MarketSeer Backend Server Stopped")
