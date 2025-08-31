# MarketSeer 数据工作流系统

## 概述

MarketSeer 数据工作流系统提供了从数据收集到存储的完整自动化解决方案。系统支持多数据源收集、智能容错、批量处理和自动备份等功能。

## 架构组件

### 1. 工作流管理器 (WorkflowManager)

-   统一管理所有数据工作流
-   协调收集器和存储器
-   提供高级别的工作流接口

### 2. 股票工作流 (StockWorkflow)

-   专门处理股票数据的工作流
-   支持基本信息收集和历史数据收集
-   实现智能容错和批量处理

### 3. 数据收集器

-   Tushare 收集器：专业金融数据
-   AKShare 收集器：开源金融数据
-   yfinance 收集器：国际市场数据

### 4. 存储系统

-   MySQL 数据库存储结构化数据
-   文件系统备份原始数据
-   支持中文注释和字符编码

## 快速开始

### 1. 环境配置

确保已安装所需依赖：

```bash
pip install -r requirements.txt
```

配置环境变量：

```bash
# 设置数据库密码
export MYSQL_PASSWORD=your_password

# 设置数据源Token（可选）
export TUSHARE_TOKEN=your_tushare_token
```

### 2. 数据库初始化

执行 SQL 脚本创建数据表：

```bash
mysql -u root -p marketseer < scripts/create_stocks_table.sql
```

### 3. 运行工作流

使用演示脚本：

```bash
python scripts/run_workflow.py
```

## 使用示例

### 基本用法

```python
import asyncio
from src.data.workflows.workflow_manager import WorkflowManager

async def main():
    # 创建工作流管理器
    manager = WorkflowManager()

    # 初始化
    await manager.initialize()

    # 收集指定股票信息
    result = await manager.run_stock_info_collection(
        symbols=['000001.SZ', '600000.SH'],
        preferred_collector='tushare',
        batch_size=10
    )

    print(f"处理结果: {result}")

    # 清理资源
    await manager.cleanup()

# 运行
asyncio.run(main())
```

### 历史数据收集

```python
from datetime import datetime, timedelta

async def collect_historical_data():
    manager = WorkflowManager()
    await manager.initialize()

    # 收集最近一周的历史数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    result = await manager.run_historical_data_collection(
        symbols=['000001.SZ', '600000.SH'],
        start_date=start_date,
        end_date=end_date,
        preferred_collector='yfinance'
    )

    await manager.cleanup()
    return result
```

### 每日更新工作流

```python
async def daily_update():
    manager = WorkflowManager()
    await manager.initialize()

    # 更新现有股票的基本信息
    result = await manager.run_daily_update()

    await manager.cleanup()
    return result
```

## 工作流类型

### 1. 股票基本信息收集工作流

**功能**：

-   收集股票的基本信息（代码、名称、行业等）
-   支持指定股票列表或全市场扫描
-   批量处理和容错机制

**使用场景**：

-   初始化股票数据库
-   定期更新股票基本信息
-   新股上市信息收集

### 2. 历史数据收集工作流

**功能**：

-   收集指定时间段的历史价格数据
-   支持多种数据源切换
-   自动保存到文件系统

**使用场景**：

-   历史数据回测
-   技术分析数据准备
-   数据备份和归档

### 3. 每日更新工作流

**功能**：

-   自动检测现有数据
-   增量更新股票信息
-   适合定时任务调度

**使用场景**：

-   每日数据维护
-   自动化数据更新
-   系统健康检查

### 4. 完整更新工作流

**功能**：

-   全市场股票列表更新
-   完整的基本信息刷新
-   适合系统重建

**使用场景**：

-   系统初始化
-   数据库重建
-   定期完整同步

## 配置说明

### 工作流配置

在 `config/config.yaml` 中配置：

```yaml
# 数据源配置
data_sources:
    tushare:
        token: ${TUSHARE_TOKEN}
        timeout: 30
        retry_count: 3

    akshare:
        timeout: 30
        retry_count: 3

    yfinance:
        timeout: 30
        retry_count: 3

# 数据库配置
database:
    mysql:
        host: localhost
        port: 3306
        database: marketseer
        username: root
        password: ${MYSQL_PASSWORD}
```

### 批处理配置

```python
# 调整批处理大小（根据系统性能）
batch_size = 50  # 每批处理的股票数量

# 调整请求间隔（避免限频）
request_delay = 1  # 秒
```

## 错误处理

### 数据源容错

系统会自动在多个数据源间切换：

1. 优先使用指定的首选收集器
2. 如果失败，自动尝试其他收集器
3. 记录详细的错误信息

### 存储容错

存储系统具备回退机制：

1. 优先尝试批量存储
2. 如果失败，切换为逐个存储
3. 自动备份到文件系统

### 限频处理

针对 API 限频的处理策略：

1. 检测限频错误
2. 自动等待和重试
3. 动态调整请求频率

## 监控和日志

### 系统状态检查

```python
# 获取系统状态
status = manager.get_system_status()
print(f"收集器状态: {status['collectors']}")
print(f"存储器连接: {status['storage_connected']}")
```

### 日志配置

日志文件位置：

-   `logs/app.log` - 应用程序日志
-   `logs/error.log` - 错误日志
-   `logs/database.log` - 数据库日志

### 处理结果统计

每个工作流都会返回详细的处理统计：

```python
{
    'total': 100,      # 总处理数量
    'success': 95,     # 成功数量
    'failed': 5,       # 失败数量
    'errors': [...]    # 错误详情列表
}
```

## 性能优化

### 批处理优化

-   根据网络环境调整批处理大小
-   平衡处理速度和系统稳定性
-   避免过于频繁的数据库连接

### 内存管理

-   及时清理资源
-   使用异步处理避免阻塞
-   合理设置连接池大小

### 网络优化

-   设置合理的超时时间
-   实现重试机制
-   使用连接复用

## 扩展开发

### 添加新的收集器

1. 继承 `BaseCollector` 类
2. 实现必要的接口方法
3. 注册到工作流管理器

### 添加新的工作流

1. 创建新的工作流类
2. 实现工作流逻辑
3. 集成到管理器中

### 自定义存储后端

1. 实现存储接口
2. 添加配置支持
3. 更新工作流集成

## 故障排除

### 常见问题

1. **数据库连接失败**

    - 检查配置文件
    - 确认数据库服务状态
    - 验证连接参数

2. **API 访问失败**

    - 检查网络连接
    - 验证 API Token
    - 查看限频策略

3. **数据格式错误**
    - 检查数据源格式变化
    - 更新数据类型定义
    - 验证字段映射

### 调试模式

启用调试日志：

```python
import logging
logging.getLogger('src.data').setLevel(logging.DEBUG)
```

## 最佳实践

1. **定期备份数据**
2. **监控系统状态**
3. **及时更新依赖**
4. **合理设置限频**
5. **使用异步处理**
6. **实现优雅关闭**

## 贡献指南

欢迎贡献代码和建议！请参考项目的贡献指南。
