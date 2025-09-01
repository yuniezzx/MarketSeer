# 将 akshare 接口写入本地数据库 — 实施计划

## 一、前提与假设

-   项目使用 SQLAlchemy，已配置多种数据库（默认 SQLite，可切换为 MySQL/Postgres），配置见 `config/database.py`。
-   akshare 作为数据源，返回 `pandas.DataFrame`。
-   目标：可靠、可扩展地把 akshare 的不同 endpoint 数据写入本地数据库，支持增量、重试、调度与监控。

---

## 二、总体架构（模块划分）

-   `akshare_client`：封装 akshare 调用，包含重试、超时、限频、参数化拉取接口。
-   `models`：SQLAlchemy ORM 模型（每类数据一张表）。
-   `repositories`：持久化层，提供 `bulk_upsert`、`bulk_insert`、checkpoint 读写接口。
-   `etl`：DataFrame -> ORM 映射、字段清洗、类型与校验。
-   `tasks`：任务执行逻辑（一次拉取流程的编排）。
-   `scheduler`：定期调度（APScheduler 或 Celery）。
-   `migrations`：Alembic 管理数据库迁移。
-   `tests`：单元与集成测试（使用 SQLite 内存 DB）。

---

## 三、关键设计决策

-   Upsert：MySQL 使用 `ON DUPLICATE KEY UPDATE`；Postgres 使用 `ON CONFLICT`；SQLite 使用 UPSERT 或 SQLAlchemy `merge`。在 repository 层封装 DB 特定逻辑。
-   Checkpoint：维护 `ingest_metadata(endpoint TEXT PRIMARY KEY, last_fetched TIMESTAMP, params JSON)`，用于增量拉取。
-   批量写入：按批次（例如 500-2000 行）提交，减少事务开销。
-   错误处理：使用重试（推荐 `tenacity`），失败写入错误表并触发告警。
-   事务：每次批量写入使用事务，保证原子性。
-   并发控制：避免同时写入同一表导致冲突；使用队列或锁。

---

## 四、建议依赖

-   akshare
-   pandas
-   sqlalchemy
-   alembic
-   pymysql / psycopg2-binary
-   apscheduler 或 celery + redis
-   tenacity
-   python-dotenv
-   pytest

---

## 五、目录建议

-   `src/akshare_client.py`
-   `src/models/__init__.py`
-   `src/models/stock.py`
-   `src/repositories/stock_repo.py`
-   `src/etl/stock_etl.py`
-   `src/tasks/ingest_task.py`
-   `src/scheduler.py`
-   `migrations/`
-   `tests/`
-   `docs/akshare_ingest.md`（本文件）

---

## 六、示例表设计（以 A 股日线为例）

表名：`stock_zh_a_daily`  
主键：`(ts_code, trade_date)`（联合唯一索引）  
主要字段：`ts_code, trade_date (date), open, high, low, close, volume, turnover, created_at, updated_at`

创建 checkpoint 示例：

```sql
CREATE TABLE IF NOT EXISTS ingest_metadata (
  endpoint TEXT PRIMARY KEY,
  last_fetched TIMESTAMP,
  params JSON,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 七、实现步骤（含时间估算）

1. 确认目标 endpoints 与采集频率（0.5d）
2. 建表与 SQLAlchemy 模型 + Alembic 初始迁移（0.5–1d）
3. 实现 `akshare_client`（封装接口、重试、超时）（1d）
4. 实现 ETL 层（DataFrame 清洗与类型转换）（1d）
5. 实现 repository（bulk upsert、checkpoint 接口）（0.5–1d）
6. 集成并测试一个端到端任务（从 checkpoint 拉取 → 写入 → 更新 checkpoint）（0.5–1d）
7. 添加调度（APScheduler 或 Celery）与运行脚本（0.5–1d）
8. 编写测试与 CI（pytest + GitHub Actions）（1d）
9. 监控与告警、备份策略（0.5d）

---

## 八、实现细节与注意事项

-   时间统一使用 UTC 存储，展示时转换为本地时区。
-   处理 DataFrame 的 NaN/inf 为 NULL 或默认值。
-   大表写入时考虑分区、索引与批量写入大小调优。
-   测试通过 mock akshare 返回并用 SQLite 内存 DB 做集成测试。

---

## 九、交付物

-   可运行的 ETL 脚本（单次与调度）
-   SQLAlchemy 模型与 Alembic 迁移文件
-   repository（upsert/bulk）实现与 checkpoint 表
-   测试用例与 CI 配置
-   README（环境变量、运行说明、故障排查）

---

## 十、下一步（在 Act 模式执行）

-   在 Act 模式中，我会创建 `docs/akshare_ingest.md` 并写入本内容；或按你指定的路径/命名创建。
-   第一步建议在 Act 模式实现并测试一个 endpoint（例如 `stock_zh_a_daily`）端到端。
