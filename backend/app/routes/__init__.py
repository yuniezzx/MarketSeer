"""
路由模块
"""

from flask import Blueprint

# 创建 API 蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入路由
from app.routes import stocks, lhb

__all__ = ['api_bp']
