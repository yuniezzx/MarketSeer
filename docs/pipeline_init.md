# Pipeline — Init 与 raw_stock_source 操作说明

## 1. init（初始化表结构）

目的

- 在新环境或升级时创建/保证所需数据库表与索引存在。init 模块集中管理可注册的表初始化函数，便于按需初始化单表或一次性初始化全部表。

位置与入口

- 实现文件：`pipeline/init.py`
- 注册逻辑：模块顶部维护 `_REGISTRY`，使用 `@register("table_name")` 将初始化函数加入注册表。
- 常用函数：`init_tables(names)`、`init_all()`。

常用 CLI 用法

- 初始化单个或多个表（按注册名）：

```bash
# 初始化 raw_stock_source 表
python -m pipeline.init --tables raw_stock_source

# 初始化 stock_basic 与 raw_stock_source
python -m pipeline.init --tables stock_basic raw_stock_source

# 初始化所有已注册的表
python -m pipeline.init --all
```

实现要点

- 每个 init 函数应是幂等的（使用 `CREATE TABLE IF NOT EXISTS`、`CREATE INDEX IF NOT EXISTS` 等），以便多次运行不会失败或重复建表。
- init 函数内部使用 `get_engine()` 获得 SQLAlchemy 引擎并在短事务内执行 SQL（见 `pipeline/init.py` 示例实现）。
- 默认命令（不带参数时）会初始化 `stock_basic`（可在 CLI 中覆盖）。

开发/排错提示

- 若表未按预期创建，先查看 `get_engine()` 返回的 DB URL（确认 DB_TYPE/环境变量），并在数据库中手动执行 `SELECT sql FROM sqlite_master WHERE type='table' AND name='raw_stock_source';` 检查表定义。
- 若需要扩展：在 `pipeline/init.py` 新增函数并用 `@register("your_table")` 装饰。

---

## 2. stock_basic（股票基本信息表）

目的

- 存储股票的基本信息，包括公司信息、财务数据、交易所信息等综合数据。数据来源于多个数据源（akshare / efinance）的整合。

表结构（在 `schema/stock_basic.sql` 中定义）

- 表名：`stock_basic`
- 主要栏位：
  - `symbol TEXT NOT NULL PRIMARY KEY` — 股票代码
  - `name TEXT` — 股票名称
  - `short_name TEXT` — 股票简称
  - `exchange TEXT` — 交易所
  - `industry TEXT` — 行业
  - `list_date TEXT` — 上市日期（字符串）
  - `listed_date INTEGER` — 上市时间（时间戳）
  - `total_shares REAL` — 总股本
  - `float_shares REAL` — 流通股
  - `total_market_cap REAL` — 总市值
  - `float_market_cap REAL` — 流通市值
  - 以及更多公司详细信息字段（见 schema/stock_basic.sql）

索引

- `idx_stock_symbol`：基于 `symbol` 的唯一索引

数据写入方式

- 通过 `pipeline.upsert_stock_basic.upsert_stock_basic(symbol)` 函数写入数据
- 该函数会：
  1. 从 raw_stock_source 获取三个数据源的最新数据：
     - akshare.stock_individual_info_em
     - akshare.stock_individual_basic_info_xq
     - efinance.stock.get_base_info
  2. 整合数据并映射字段名（见 pipeline/upsert_stock_basic.py 中的 FIELD_MAPPING）
  3. 使用 INSERT OR REPLACE 写入 stock_basic 表

如何执行以将数据写入 stock_basic

- 运行脚本（基础用法）：

  ```bash
  # 更新单个股票的基本信息
  python -m pipeline.upsert_stock_basic 002104

  # 也可以带上交易所后缀
  python -m pipeline.upsert_stock_basic 002104.SZ
  ```

- 运行时行为

  - 脚本会自动从 raw_stock_source 获取最新的原始数据
  - 会整合多个数据源的信息，确保数据完整性
  - 对于缺失的数据源会记录警告并继续处理
  - 特殊字段（如日期）会自动转换为合适的格式

- 检查写入结果（sqlite3 / SQL）

  ```sql
  -- 查看特定股票的基本信息
  SELECT * FROM stock_basic WHERE symbol = '002104';

  -- 查看最近更新的股票
  SELECT symbol, name, updated_at
  FROM stock_basic
  ORDER BY updated_at DESC
  LIMIT 10;
  ```

- 数据更新提示
  - 建议先确保 raw_stock_source 有最新数据（使用 pipeline.ingest）
  - 更新频率应依据数据实时性需求，但通常不需要高频更新
  - 可以通过 updated_at 字段追踪数据更新时间

## 3. raw_stock_source（原始数据归档表）

目的

- 存储从数据客户端（akshare / efinance 等）抓取到的原始响应（JSON/text），用于审计、回放与下游解析。

表结构（在 `pipeline/init.py` 中定义）

- 表名：`raw_stock_source`
- 栏位：
  - `id INTEGER PRIMARY KEY AUTOINCREMENT` — 自增主键
  - `symbol TEXT` — 相关股票标识（若可用）
  - `source TEXT` — 数据源（例如 `akshare` / `efinance`）
  - `endpoint TEXT` — 调用的客户端接口名
  - `raw TEXT` — 原始 JSON / 文本响应
  - `fetched_at INTEGER` — Unix 时间戳（秒）

索引

- `idx_raw_symbol`：基于 `symbol` 的普通索引（便于按 symbol 查询）。

写入方式（来自 pipeline.ingest）

- `pipeline.ingest.ingest_for_symbol(...)` 会调用客户端，得到 pandas 结构或原始对象，转换为 JSON（保留中文字符 `ensure_ascii=False`）并通过 `insert_raw_stock_source(...)` 写入该表。
- 注意：`ingest.py` 中会根据 endpoint 需要调整传参格式（plain / prefixed / full），并在异常时记录警告而非中断整个任务。

如何执行以将数据写入 raw_stock_source

- 运行脚本（基础用法）：

  - 指定一个或多个 symbol （可带或不带交易所后缀）：
    ```bash
    python -m pipeline.ingest --symbols 002104.SZ
    python -m pipeline.ingest --symbols 002104 600000.SH
    ```
  - 默认样本 symbols（如果不传 `--symbols`）：
    ```bash
    python -m pipeline.ingest
    ```
  - 可设置请求间隔（避免被数据源限流）：
    ```bash
    python -m pipeline.ingest --symbols 002104 --delay 0.5
    ```

- 运行时行为要点

  - 脚本会先调用 `get_engine()` 确保数据库可用，然后对每个 endpoint 调用相应客户端并把响应写入 `raw_stock_source`。
  - 如果 symbol 不带后缀，脚本会尝试根据代码首位推断交易所（以 `6` 开头推断为 `SH`，否则 `SZ`），并为不同 endpoint 选择合适的符号格式。
  - 单个 endpoint 调用失败会记录警告并继续下一个 endpoint，而不会中断整个 ingest 流程。
  - 为排查问题，可以把日志级别调为 DEBUG（在脚本顶部或运行环境中调整），查看尝试的参数组合与具体异常。

- 检查写入结果（sqlite3 / SQL）

  - 查看最近插入的行（按 fetched_at 或 id 排序）：
    ```sql
    SELECT * FROM raw_stock_source ORDER BY fetched_at DESC LIMIT 20;
    ```
  - 按 symbol 过滤：
    ```sql
    SELECT * FROM raw_stock_source WHERE symbol='002104' OR symbol='002104.SZ' ORDER BY fetched_at DESC LIMIT 50;
    ```
  - 查看特定 endpoint 的原始文本（raw 列为 JSON string）：
    ```sql
    SELECT id, symbol, source, endpoint, fetched_at, raw
    FROM raw_stock_source
    WHERE endpoint='stock.get_base_info'
    ORDER BY fetched_at DESC LIMIT 10;
    ```

- 读入 raw 字段（示例）

  - raw 字段保存的是 JSON 字符串；在 Python 中可以用：
    ```python
    import json
    # raw_text 从 DB 读取
    obj = json.loads(raw_text)
    ```

- 插入函数与代码位置

  - 写入是通过 `pipeline.helper.insert_raw_stock_source(...)` 完成的；如需修改写入行为或验证事务，请查看 `pipeline/helper.py`。

- 干跑 / 调试建议（避免写入 DB）

  - 当前脚本没有内置 --dry-run 标志。想要“预览”将调用哪些 endpoint 和参数，可：
    - 临时把 `insert_raw_stock_source` 调用替换为打印函数，或
    - 在 `pipeline.ingest` 中把 `insert_raw_stock_source` 用一个 mock 函数替换（用于本地调试）。
  - 另一种简单方式是把数据库连接换成临时 SQLite 文件（设置环境变量 `SQLITE_PATH` 指向一个临时文件），运行脚本后删除该文件以清理测试数据。

- 常见问题排查
  - 如果发现写入没有发生，先检查 `get_engine()` 配置（确认 `DB_TYPE` / `SQLITE_PATH` / 环境变量）并查看脚本日志。
  - 如果 raw 中字段缺失或结构不对，可能是客户端返回的 DataFrame 以 index 表示字段名（脚本会尝试把单列 DataFrame 的 index 转为 key->value 映射）；请把该 raw 的内容贴出来以便进一步诊断。

自增 id 与删除行后的行为

- SQLite 的 `AUTOINCREMENT` 会记录在 `sqlite_sequence` 中，删除表中若干行不会自动减少 `id`。这是数据库正常行为：删除不会回退自增计数器。
- 想“回退”或“重新开始记数”的可选方案：

  1. 同步 seq 为当前最大 id（非破坏性，推荐）：

     ```sql
     -- 查看最大 id
     SELECT COALESCE(MAX(id), 0) FROM raw_stock_source;

     -- 将 sqlite_sequence.seq 设置为当前最大 id，使下次插入从 max(id)+1 开始
     UPDATE sqlite_sequence
     SET seq = (SELECT COALESCE(MAX(id), 0) FROM raw_stock_source)
     WHERE name = 'raw_stock_source';

     -- 验证
     SELECT seq FROM sqlite_sequence WHERE name='raw_stock_source';
     ```

  2. 若表为空且希望从 1 开始，可删除 sqlite_sequence 对应行（风险较小，需确认表为空）：
     ```sql
     DELETE FROM sqlite_sequence WHERE name = 'raw_stock_source';
     ```
     然后下一条插入会从 1 或最小可用 ROWID 开始（请先备份）。
  3. 彻底重建表以重新编号所有行（破坏性，高风险，需备份与同步外键）。

- 我已提供了一个小脚本用于备份并更新 sqlite_sequence：`tools/reset_sqlite_seq.py`（项目根目录下），可在本地运行以将 sqlite_sequence.seq 同步为当前最大 id。

操作前必读（安全步骤）

1. 备份数据库（强制）：复制 `data/marketseer.db` 到安全位置。
2. 确认是否存在外键或外部引用到 `raw_stock_source.id`（若有，不建议更改已有 id）。
3. 先在 dev 环境验证 SQL，再在生产环境执行。
4. 若你希望我替你执行（备份 + 更新 seq 或重建表），请切换到 Act mode 并确认允许执行写操作。

---

附录：快速检查命令（sqlite3 CLI）

- 打开 DB：

```bash
sqlite3 data/marketseer.db
```

- 查看表定义：

```sql
SELECT sql FROM sqlite_master WHERE type='table' AND name='raw_stock_source';
```

- 查看最大 id：

```sql
SELECT COALESCE(MAX(id),0) FROM raw_stock_source;
```

- 查看 sqlite_sequence：

```sql
SELECT * FROM sqlite_sequence WHERE name='raw_stock_source';
```
