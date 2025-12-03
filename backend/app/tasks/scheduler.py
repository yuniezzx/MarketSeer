"""
APScheduler 调度器初始化
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import current_app
from app.config import Config
from app.tasks.jobs.intraday_update import fetch_intraday_data

scheduler = BackgroundScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(url=Config.SQLALCHEMY_DATABASE_URI)
    },
    executors={
        'default': ThreadPoolExecutor(10)
    },
    job_defaults={
        'coalesce': False,
        'max_instances': 1
    },
    timezone='Asia/Shanghai'
)

def start_scheduler():
    if not scheduler.running:
        # 注册分时数据获取任务 - 每5分钟执行一次
        scheduler.add_job(
            func=fetch_intraday_data,
            trigger='cron',
            minute='*/5',
            hour='9-15',
            day_of_week='mon-fri',
            args=[current_app._get_current_object()],
            id='fetch_intraday_data',
            replace_existing=True,
            name='获取追踪股票分时数据'
        )
        
        scheduler.start()
