"""
MarketSeer 后端启动脚本
"""

from app import create_app
from config import Config
from logger import logger


config = Config()

# 创建 Flask 应用
app = create_app()


if __name__ == '__main__':
    # 获取环境变量配置
    env = config.ENV
    host = config.FLASK_HOST
    port = config.FLASK_PORT
    debug = config.FLASK_DEBUG

    logger.info("=" * 60)
    logger.info("MarketSeer 后端服务启动中...")
    logger.info(f"开发模式 : {'开发环境' if env == 'development' else '生产环境'}")
    logger.info(f"Debug: {debug}")
    logger.info(f"API Base URL: http://{host}:{port}/api")
    logger.info("=" * 60)

    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.warning("收到停止信号，正在关闭服务...")
    except Exception as e:
        logger.exception(f"服务启动失败: {e}")
    finally:
        logger.info("MarketSeer 后端服务已停止")
