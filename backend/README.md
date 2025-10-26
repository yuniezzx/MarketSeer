# MarketSeer Backend

MarketSeer 后端服务 - 金融数据采集、整合与分析系统

## 技术栈

- **框架**: Flask 3.0+
- **数据库**: SQLite + SQLAlchemy ORM
- **数据源**: AkShare, eFinance, yFinance
- **Python**: 3.9+

## 项目结构

```
backend/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── config.py            # 配置文件
│   ├── models/              # 数据库模型
│   ├── routes/              # API 路由
│   ├── services/            # 业务逻辑层
│   ├── utils/               # 工具函数
│   └── tasks/               # 定时任务
├── data/                    # 数据库文件目录
├── logs/                    # 日志文件目录
├── run.py                   # 启动脚本
└── pyproject.toml           # uv 项目配置
```

## 快速开始

### 1. 安装 uv（如果还未安装）

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 创建虚拟环境并安装依赖

```bash
cd backend
uv venv
uv pip install -e .
```

### 3. 激活虚拟环境

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 4. 运行后端服务

```bash
python run.py
```

服务将在 http://localhost:5000 启动

## API 接口

### 健康检查

```
GET /api/health
```

### 股票列表

```
GET /api/stocks?page=1&per_page=50&market=SH&industry=金融
```

### 股票详情

```
GET /api/stocks/{code}
```

### 搜索股票

```
GET /api/stocks/search?keyword=茅台
```

### 更新股票数据

```
POST /api/update/stocks
Content-Type: application/json

{
  "source": "all"  // 可选: "akshare", "efinance", "all"
}
```

## 环境配置

### .env 文件配置

项目使用 `.env` 文件进行配置管理。首先复制示例配置文件：

```bash
cp .env.example .env
```

然后根据需要修改 `.env` 文件中的配置项：

```bash
# Flask 配置
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# 服务器配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 数据库配置 (可选，默认使用 SQLite)
# SQLALCHEMY_DATABASE_URI=sqlite:///data/marketseer.db

# 数据源配置 (可选，默认启用 akshare 和 efinance)
# DATA_SOURCES_AKSHARE_ENABLED=True
# DATA_SOURCES_AKSHARE_PRIORITY=1
# DATA_SOURCES_EFINANCE_ENABLED=True
# DATA_SOURCES_EFINANCE_PRIORITY=2
# DATA_SOURCES_YFINANCE_ENABLED=False
# DATA_SOURCES_YFINANCE_PRIORITY=3

# 数据更新配置 (可选，默认 3600 秒)
# UPDATE_INTERVAL=3600

# 日志配置 (可选)
# LOG_LEVEL=INFO

# CORS 配置 (可选，默认允许 localhost:3000 和 localhost:5173)
# CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**注意**: `.env` 文件已被添加到 `.gitignore`，不会被提交到版本控制中。请妥善保管生产环境的 `.env` 文件。

## 开发指南

### 添加新的数据模型

1. 在 `app/models/` 创建新的模型文件
2. 在 `app/models/__init__.py` 中导入
3. 运行应用自动创建表

### 添加新的 API 路由

1. 在 `app/routes/` 创建新的路由文件
2. 在 `app/routes/__init__.py` 中导入
3. 使用蓝图注册路由

### 添加新的数据服务

1. 在 `app/services/` 创建新的服务文件
2. 实现数据采集和处理逻辑
3. 在路由中调用服务

## 数据库

数据库文件位于 `data/marketseer.db`

初次运行时会自动创建数据库和表结构。

## 日志

日志文件位于 `logs/marketseer.log`

日志级别可在 `config.py` 中配置。

## 测试

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
pytest
```

## 许可证

MIT License
