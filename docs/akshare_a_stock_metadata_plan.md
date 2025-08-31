# A 股 — 使用 Akshare 获取股票基本信息（计划文档）

目的

-   使用 Akshare 作为首个数据源，先实现获取 A 股的“股票基本信息”（stock_info / metadata），后续再扩展到行情/日线等数据接口（例如 `stock_sse_deal_daily`）。
-   采用 Adapter 模式，实现可测试、可复用的适配层，保存原始数据并将清洗后的数据写入 ORM（models/stock.py）。

总体流程

1. 确认数据源与范围
    - 数据源：Akshare（仅 A 股，后续可扩展）
    - 首批目标：获取所有可交易股票的基本信息（代码、名称、上市日、所属行业、总股本等）
2. 设计适配器接口（Adapter）
    - 定义统一抽象（DataAdapter），方法示例：
        - fetch_metadata(symbols=None) -> pandas.DataFrame / list[dict]
        - fetch_price(symbol, start, end) -> pandas.DataFrame
        - fetch_realtime(symbol) -> dict（可选）
    - 约定返回字段：包含 source、fetched_at、raw_payload
3. 实现 akshare 适配器（adapters/akshare_adapter.py）
    - 使用 akshare 的 API 拉取基础信息（A 股列表 + 单只股票详情）
    - 处理分页 / 限速 / 重试
    - 保存 raw（data/raw/akshare/YYYY-MM-DD/\*.json 或 .csv）
4. 清洗与映射（transform）
    - 将 akshare 原始字段映射到本项目的标准字段（参见 `models/stock.py`）
    - 校验必填字段与数据类型（code/symbol/name/listing_date 等）
5. 持久化（upsert）
    - 对 `stock_info` 表使用 upsert（以 (market, code) 或 ISIN 作为键）
    - 在写入前后记录 `last_sync_time`
6. 调度与监控
    - 本阶段可用本地脚本/cron 调度；生产建议用 Celery / Airflow
    - 增加重试与告警（接口异常/空数据/字段缺失）
7. 测试
    - 单元测试：mock akshare 返回，验证 transform 与 upsert
    - 集成测试：小批量真实数据跑通到数据库

示例目录结构（建议）

-   adapters/
    -   akshare_adapter.py
-   pipelines/
    -   transform_metadata.py
    -   upsert_metadata.py
-   data/raw/akshare/
-   docs/
    -   akshare_a_stock_metadata_plan.md
-   tests/
    -   test_akshare_adapter.py
    -   test_transform_metadata.py

示例实现草案（Python，概念性示例）

```python
# language: python
from datetime import datetime
import json
import pandas as pd
import akshare as ak
from sqlalchemy.exc import IntegrityError
from models import StockInfo
from config.database import SessionLocal

class AkshareAdapter:
    source = "akshare"

    def fetch_a_stock_list(self) -> pd.DataFrame:
        """
        拉取 A 股代码/名称列表（示例函数名，请根据本地 akshare 版本确认实际接口）
        """
        # 示例：ak.stock_info_a_code_name() 或者其他接口
        df = ak.stock_info_a_code_name()
        df["fetched_at"] = datetime.utcnow()
        return df

    def fetch_stock_detail(self, code: str) -> dict:
        """
        拉取单只股票的详细信息（若需要）
        """
        # 示例：使用 ak 的相关接口获取单股详情
        detail = {}  # 替换为真实调用结果
        return detail

def save_raw(df: pd.DataFrame, path: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(path, orient="records", force_ascii=False, date_format="iso")

def transform_ak_to_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    将 akshare 返回的 columns 映射到 models/stock.py 中的字段名
    例如：code -> code, name -> name, list_date -> listing_date 等
    """
    mapping = {
        "代码": "code",
        "名称": "name",
        # 根据实际字段填写映射
    }
    df = df.rename(columns=mapping)
    # 转换类型
    if "listing_date" in df.columns:
        df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce").dt.date
    df["market"] = "SH/SZ"  # 根据 code 判断市场
    return df

def upsert_stock_info(df: pd.DataFrame):
    session = SessionLocal()
    for _, row in df.iterrows():
        try:
            obj = session.query(StockInfo).filter_by(market=row["market"], code=row["code"]).one_or_none()
            if obj is None:
                obj = StockInfo(
                    symbol=f"{row['code']}.{row['market']}",
                    code=row["code"],
                    market=row["market"],
                    name=row.get("name"),
                    listing_date=row.get("listing_date"),
                    # 其他字段...
                )
                session.add(obj)
            else:
                # 更新可变字段
                obj.name = row.get("name") or obj.name
                obj.listing_date = row.get("listing_date") or obj.listing_date
            session.commit()
        except IntegrityError:
            session.rollback()
        except Exception:
            session.rollback()
            raise
    session.close()
```

注意事项 / 小贴士

-   在开始实现前，请先在本地确认你安装的 akshare 版本及可用的接口名称（示例接口名在不同版本可能不同）。可在 Python REPL 执行 `import akshare as ak; dir(ak)` 或查阅 akshare 官方文档。
-   为避免重复写入，使用表上的 UniqueConstraint（在 `models/stock.py` 已添加）并在写入时采用 upsert/merge 或先查询再更新的策略。
-   保存原始数据以便追溯（尤其在对接第三方时很重要）。
-   对于 A 股代码，判断市场可以根据代码前缀或使用 akshare 提供的市场字段。

初始任务清单（已更新）

-   [x] 确认数据源与频率（A 股 / Akshare；首阶段：基础信息，日级或一次性全量）
-   [ ] 设计 DataAdapter 抽象接口
-   [ ] 实现 Akshare Adapter（fetch_metadata）
-   [ ] 实现 transform + upsert（metadata -> models/stock.py）
-   [ ] 编写单元测试与集成测试
-   [ ] 部署调度与监控

下一步（请在下面选一项）

-   我开始在 Act Mode 中创建 `adapters/akshare_adapter.py` 与 pipelines 模板（请选择并切换到 "Act mode"）
-   你先确认 akshare 版本并告诉我可用接口名称（我据此实现具体调用）
-   或者我先生成一个基于假定接口的适配器草稿（无需切换到 Act Mode），你再调整接口名后我在 Act Mode 应用修改
