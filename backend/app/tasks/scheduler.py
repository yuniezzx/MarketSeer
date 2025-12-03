"""
APScheduler 调度器初始化
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import current_app
from config import Config

scheduler = BackgroundScheduler(
    jobstores={'default': SQLAlchemyJobStore(url=Config.SQLALCHEMY_DATABASE_URI)},
    executors={'default': ThreadPoolExecutor(10)},
    job_defaults={'coalesce': False, 'max_instances': 1},
    timezone='Asia/Shanghai',
)
