# Models 模块架构说明

## 📁 目录结构

```
backend/app/models/
├── __init__.py              # 模型统一导出和初始化
├── base.py                  # 基础模型类和 db 实例
├── README.md                # 详细开发文档
├── ARCHITECTURE.md          # 本文档（架构说明）
├── stock/                   # 股票相关模型
│   ├── __init__.py
│   ├── stock_info.py        # 股票基本信息
│   ├── stock_daily.py       # 股票日线数据
│   └── stock_minute.py      # 股票分钟级数据
└── market/                  # 市场相关模型
    ├── __init__.py
    ├── index_info.py        # 指数信息
    └── sector_info.py       # 板块/行业信息
```

## 🏗️ 架构设计

### 1. 基础设施层 (base.py)

**BaseModel 抽象基类**

- 所有业务模型的基类
- 提供通用字段：id、created_at、updated_at
- 提供通用方法：to_dict()、save()、delete()、get_by_id()、get_all()、count()
- 使用 `__abstract__ = True` 标记，不创建实际表

**数据库实例 (db)**

- 全局 SQLAlchemy 实例
- 在 application factory 中延迟初始化

**初始化函数 (init_db)**

- 确保 data 目录存在
- 创建所有表结构

### 2. 业务模型层

#### Stock 模块（股票相关）

**StockInfo - 股票基本信息**

- 存储股票代码、名称、市场、行业等基本信息
- 索引：code (unique)、market、industry
- 复合索引：(market, code)
- 查询方法：get_by_code()、get_by_market()、get_by_industry()、search_by_name()

**StockDaily - 股票日线数据**

- 存储每日 OHLC 数据、成交量、成交额、涨跌幅等
- 唯一约束：(stock_code, trade_date)
- 索引：stock_code、trade_date
- 查询方法：get_by_code_and_date()、get_date_range()、get_latest()

**StockMinute - 股票分钟数据**

- 存储分钟级 OHLC 数据
- 唯一约束：(stock_code, trade_date, trade_time)
- 复合索引：(stock_code, trade_date, trade_time)
- 查询方法：get_by_code_and_datetime()、get_by_code_and_date()、get_datetime_range()

#### Market 模块（市场相关）

**IndexInfo - 指数信息**

- 存储市场指数基本信息（上证指数、深证成指等）
- 索引：code (unique)、market、index_type
- 复合索引：(market, index_type)
- 查询方法：get_by_code()、get_by_market()、get_by_type()

**SectorInfo - 板块/行业信息**

- 存储行业板块、概念板块分类信息
- 支持层级结构（parent_code、level）
- 索引：code (unique)、sector_type、parent_code
- 复合索引：(sector_type, level)
- 查询方法：get_by_code()、get_by_type()、get_by_parent()、get_top_level()

## 🔑 核心特性

### 1. 模块化设计

- 按业务领域组织（stock/、market/）
- 每个子模块有独立的 `__init__.py`
- 便于扩展新的业务领域（如 financial/、analysis/）

### 2. 统一的基类

- 所有模型继承 BaseModel
- 自动提供 id、时间戳字段
- 统一的 CRUD 方法接口

### 3. 丰富的查询方法

- 每个模型提供业务相关的查询方法
- 类方法封装常用查询逻辑
- 支持复杂查询场景

### 4. 数据完整性

- 合理的字段约束（nullable、unique）
- 外键关系（预留扩展）
- 复合索引优化查询性能

### 5. 类型安全

- 使用 Numeric 类型存储金额和价格（高精度）
- BigInteger 存储大数值（成交量）
- 明确的字段类型定义

## 📊 数据库表结构

### stock_info（股票基本信息）

```sql
- id: Integer (PK)
- code: String(20) UNIQUE NOT NULL
- name: String(100) NOT NULL
- market: String(20) NOT NULL
- industry: String(50)
- created_at, updated_at: DateTime
```

### stock_daily（股票日线数据）

```sql
- id: Integer (PK)
- stock_code: String(20) NOT NULL
- trade_date: String(20) NOT NULL
- open, high, low, close: Numeric(10,2)
- volume: BigInteger
- amount: Numeric(20,2)
- UNIQUE(stock_code, trade_date)
```

### stock_minute（股票分钟数据）

```sql
- id: Integer (PK)
- stock_code: String(20) NOT NULL
- trade_date: String(20) NOT NULL
- trade_time: String(20) NOT NULL
- open, high, low, close: Numeric(10,2)
- volume: BigInteger
- UNIQUE(stock_code, trade_date, trade_time)
```

### index_info（指数信息）

```sql
- id: Integer (PK)
- code: String(20) UNIQUE NOT NULL
- name: String(100) NOT NULL
- market: String(20) NOT NULL
- index_type: String(50)
- base_date: String(20)
- base_point: Numeric(10,2)
```

### sector_info（板块信息）

```sql
- id: Integer (PK)
- code: String(50) UNIQUE NOT NULL
- name: String(100) NOT NULL
- sector_type: String(50) NOT NULL
- parent_code: String(50)
- level: Integer
- stock_count: Integer
```

## 🚀 使用示例

### 导入模型

```python
from app.models import db, StockInfo, StockDaily, IndexInfo

# 或者导入基类
from app.models import BaseModel
```

### 查询示例

```python
# 查询股票信息
stock = StockInfo.get_by_code('000001')

# 查询日线数据
daily_data = StockDaily.get_date_range('000001', '2024-01-01', '2024-12-31')

# 搜索股票
stocks = StockInfo.search_by_name('平安')

# 获取指数
index = IndexInfo.get_by_code('000001')
```

### 创建数据

```python
# 方法1：直接创建
stock = StockInfo(
    code='000001',
    name='平安银行',
    market='SZ',
    industry='银行'
)
stock.save()

# 方法2：从字典创建
data = {'code': '000001', 'name': '平安银行', ...}
stock = StockInfo.from_dict(data)
stock.save()
```

## 🔄 扩展指南

### 添加新模型

1. 确定业务领域（stock/market/或新建目录）
2. 创建模型文件，继承 BaseModel
3. 定义表名、字段、索引
4. 实现业务查询方法
5. 在子模块 `__init__.py` 中导出
6. 在主 `__init__.py` 中添加到 `__all__`

### 添加新业务领域

1. 创建新的子目录（如 financial/）
2. 创建 `__init__.py`
3. 创建具体模型文件
4. 在主 `__init__.py` 中导入

## ✅ 设计优势

1. **清晰的结构**：按业务领域组织，易于理解和维护
2. **高度复用**：BaseModel 提供通用功能
3. **易于扩展**：模块化设计便于添加新模型
4. **性能优化**：合理的索引设计
5. **类型安全**：明确的字段类型和约束
6. **查询便利**：丰富的业务查询方法
7. **代码规范**：统一的命名和文档注释

## 📝 注意事项

1. 所有模型必须继承 BaseModel
2. 使用 `__tablename__` 明确指定表名
3. 外键字段添加索引
4. 经常查询的字段添加索引
5. 金额和价格使用 Numeric 类型
6. 日期时间统一使用字符串格式存储
7. 每个模型提供 `__repr__()` 方法
8. 覆盖 `to_dict()` 方法时处理特殊类型

## 🔮 未来规划

可根据业务需求扩展以下模块：

- **financial/**：财务报表数据
- **analysis/**：技术分析指标
- **strategy/**：交易策略相关
- **user/**：用户和权限管理
- **portfolio/**：投资组合管理
