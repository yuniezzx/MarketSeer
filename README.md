# MarketSeer - 金融数据分析平台

## 项目简介

MarketSeer 是一个专业的金融数据获取、处理和分析平台，支持多种数据源的整合，为量化投资和金融分析提供完整的数据解决方案。

## 核心特性

-   🔗 **多数据源支持**: 集成 Tushare、AKShare、yfinance 等主流金融数据 API
-   📊 **数据处理**: 完整的数据清洗、转换和分析流程
-   💾 **数据存储**: 支持 MySQL、PostgreSQL 等数据库存储
-   📋 **配置管理**: 灵活的配置文件和环境变量管理
-   📝 **日志记录**: 完整的操作日志和错误追踪
-   🧪 **测试覆盖**: 完善的单元测试和集成测试

## 项目结构

```
MarketSeer/
├── README.md                     # 项目说明文档
├── requirements.txt              # 项目依赖列表
├──
├── config/                       # 配置文件目录
│   ├── config.yaml              # 主配置文件
│   └── .env.example             # 环境变量示例文件
│
├── src/                          # 主要源代码目录
│   ├── data/                     # 数据获取和处理模块
│   │   ├── collectors/           # 数据收集器模块
│   │   │   ├── tushare_collector.py    # Tushare数据收集器
│   │   │   ├── akshare_collector.py    # AKShare数据收集器
│   │   │   └── yfinance_collector.py   # yfinance数据收集器
│   │   ├── processors/           # 数据处理器模块
│   │   │   └── data_processor.py       # 数据处理核心逻辑
│   │   └── storage/              # 数据存储模块
│   │       └── database.py             # 数据库操作接口
│   ├── utils/                    # 工具函数模块
│   │   ├── config.py            # 配置管理工具
│   │   └── logger.py            # 日志管理工具
│   └── main.py                   # 程序主入口
│
├── tests/                        # 测试代码目录
│   ├── test_data/               # 数据模块测试
│   │   └── test_collectors.py   # 数据收集器测试
│   └── test_utils/              # 工具模块测试
│       └── test_config.py       # 配置管理测试
│
├── data/                         # 数据文件目录
│   ├── raw/                     # 原始数据存储
│   ├── processed/               # 处理后数据存储
│   └── exports/                 # 导出数据存储
│
├── docs/                         # 项目文档目录
│   └── API.md                   # API文档
│
├── scripts/                      # 辅助脚本目录
│   └── setup.py                # 项目设置脚本
│
└── logs/                         # 日志文件目录
    ├── app.log                  # 应用日志
    └── error.log                # 错误日志
```

## 功能模块说明

### 数据收集器 (src/data/collectors/)

-   **Tushare 收集器**: 获取国内股票、基金、期货等金融数据
-   **AKShare 收集器**: 获取丰富的中文金融数据和新闻资讯
-   **yfinance 收集器**: 获取全球股票市场数据

### 数据处理器 (src/data/processors/)

-   数据清洗和标准化
-   技术指标计算
-   数据验证和质量检查

### 数据存储 (src/data/storage/)

-   数据库连接管理
-   数据持久化操作
-   数据查询接口

### 工具模块 (src/utils/)

-   配置文件管理
-   日志记录系统
-   通用工具函数

## 依赖说明

### 数据获取相关

-   **pandas**: 数据分析和操作的核心库
-   **numpy**: 数值计算支持
-   **requests**: HTTP 请求处理
-   **tushare**: Tushare 金融数据 API
-   **akshare**: AKShare 金融数据库
-   **yfinance**: Yahoo Finance 数据接口

### 数据库相关

-   **sqlalchemy**: 数据库 ORM 框架
-   **pymysql**: MySQL 数据库连接器
-   **psycopg2-binary**: PostgreSQL 数据库连接器

### 配置和工具

-   **python-dotenv**: 环境变量管理
-   **pyyaml**: YAML 配置文件解析
-   **loguru**: 现代化日志记录
-   **schedule**: 任务调度
-   **click**: 命令行接口

### 数据处理

-   **openpyxl**: Excel 文件操作
-   **xlrd**: Excel 文件读取

### 测试相关

-   **pytest**: 测试框架
-   **pytest-cov**: 测试覆盖率

## 安装和配置

### 1. 环境要求

-   Python 3.8+
-   pip 包管理器

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制环境变量示例文件
cp config/.env.example config/.env

# 编辑环境变量文件，配置数据库和API密钥
nano config/.env
```

### 4. 数据库配置

在`config/config.yaml`中配置数据库连接信息：

```yaml
database:
    host: localhost
    port: 3306
    username: your_username
    password: your_password
    database: marketseer
```

## 使用指南

### 基本使用

```python
from src.main import MarketSeer

# 初始化MarketSeer
ms = MarketSeer()

# 获取股票数据
stock_data = ms.get_stock_data('000001.SZ', start_date='2023-01-01')

# 处理数据
processed_data = ms.process_data(stock_data)

# 保存到数据库
ms.save_data(processed_data)
```

### 命令行使用

```bash
# 获取指定股票数据
python src/main.py --symbol 000001.SZ --start-date 2023-01-01

# 批量数据更新
python src/main.py --update-all

# 数据导出
python src/main.py --export --format csv
```

## 开发规范

### 代码组织

-   遵循 PEP 8 代码风格规范
-   使用类型提示增强代码可读性
-   模块化设计，保持低耦合高内聚

### 测试规范

-   为所有核心功能编写单元测试
-   测试覆盖率保持在 80%以上
-   使用 pytest 进行测试管理

### 日志规范

-   使用 loguru 进行统一日志管理
-   区分不同级别的日志信息
-   重要操作必须记录日志

### 版本控制

-   使用语义化版本号
-   提交信息遵循 conventional commits 规范

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

-   项目 Issues 页面
-   邮箱：your-email@example.com

---

_最后更新：2025 年 8 月 31 日_
