"""
MarketSeer 后端启动脚本
"""
import os
from app import create_app
from app.models import db

# 创建 Flask 应用
app = create_app()

# 初始化数据库
with app.app_context():
    db.init_app(app)


if __name__ == '__main__':
    # 获取环境变量配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ==========================================
    MarketSeer 后端服务启动
    ==========================================
    Host: {host}
    Port: {port}
    Debug: {debug}
    API Base URL: http://{host}:{port}/api
    ==========================================
    """)
    
    app.run(host=host, port=port, debug=debug)
