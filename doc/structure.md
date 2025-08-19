# 目录结构

```
project-root/
├─ utils/
│  ├─ __init__.py
│  ├─ config_loader.py
│  └─ logger.py                     ⭐ 可选：集中化日志
├─ data_sources/                    ⭐ 第三方数据适配层（解耦）
│  ├─ __init__.py
│  ├─ akshare_client.py             ⭐ AkShare 封装
│  └─ xq_client.py                  ⭐ 雪球/其他源封装（可选）
├─ repositories/                    ⭐ DB 读写与表结构
│  ├─ __init__.py
│  ├─ models.py                     ⭐ SQLAlchemy Table 定义
│  ├─ stock_repo.py                 ⭐ 对 stock、stock_daily 的 CRUD
│  └─ schema_migration.py           ⭐ 初始化/升级表结构
├─ jobs/                            ⭐ 任务编排（ETL/校验/告警）
│  ├─ __init__.py
│  ├─ daily_update.py               ⭐ 日常增量更新主入口
│  ├─ steps/                        ⭐ 拆分任务步骤（可独立测试）
│  │  ├─ fetch_universe.py          ⭐ 获取股票池
│  │  ├─ fetch_snapshot.py          ⭐ 拉取行情快照
│  │  ├─ upsert_basics.py           ⭐ 补全基础资料（上市日/行业等）
│  │  ├─ upsert_prices.py           ⭐ 写入/去重/幂等等价
│  │  └─ quality_checks.py          ⭐ 质量检查（缺值/异常波动）
│  └─ notify.py                     ⭐ 失败通知（邮件/钉钉/飞书，可选）
├─ scripts/                         ⭐ 命令行脚本
│  ├─ init_db.py                    ⭐ 初始化库表
│  └─ run_daily_update.py           ⭐ CLI 入口，便于 cron 调度
├─ config/
│  └─ settings.yaml                 ⭐ 补充 data 源、重试、阈值等
├─ requirements.txt
├─ .env.example
└─ Makefile
```