# MarketSeer 数据库配置指南

## 概述

本指南将帮助您配置 MarketSeer 项目的 MySQL 数据库连接。我们已经为您创建了完整的数据库管理系统，包括连接池、事务管理、日志记录等企业级功能。

## 配置步骤

### 1. 准备 MySQL 数据库

确保您的 MySQL 服务已启动，并创建项目数据库：

```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE marketseer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选，推荐）
CREATE USER 'marketseer'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON marketseer.* TO 'marketseer'@'localhost';
FLUSH PRIVILEGES;
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp config/.env.example config/.env
```

编辑 `config/.env` 文件，设置数据库密码：

```bash
# 数据库配置
MYSQL_PASSWORD=your_mysql_password_here

# 可选：其他配置覆盖
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_DATABASE=marketseer
# MYSQL_USERNAME=root
```

### 3. 检查配置文件

确认 `config/config.yaml` 中的数据库配置正确：

```yaml
database:
    mysql:
        host: localhost
        port: 3306
        database: marketseer
        username: root
        password: ${MYSQL_PASSWORD}
        charset: utf8mb4
```

### 4. 测试数据库连接

运行测试脚本验证配置：

```bash
python tests/test_database_connection.py
```

如果配置正确，您将看到：

```
✅ 数据库测试成功！
🎉 MySQL连接配置完成，可以开始使用数据库功能了！
```

## 使用方法

### 基础用法

```python
from src.data.storage.database import get_database

# 获取数据库实例
db = get_database()

# 执行查询
results = db.execute_query("SELECT * FROM your_table")

# 执行命令
affected_rows = db.execute_command("INSERT INTO your_table (col1, col2) VALUES (:val1, :val2)",
                                  {'val1': 'value1', 'val2': 'value2'})
```

### DataFrame 操作

```python
import pandas as pd
from src.data.storage.database import get_database

db = get_database()

# 查询数据到DataFrame
df = db.read_dataframe("SELECT * FROM your_table")

# 保存DataFrame到数据库
df.to_sql('new_table', db.engine, if_exists='append', index=False)
# 或使用封装方法
db.save_dataframe(df, 'new_table', if_exists='append')
```

### 使用会话管理

```python
from src.data.storage.database import database_session

# 使用上下文管理器
with database_session() as session:
    # 在这里执行数据库操作
    # 自动处理事务提交和回滚
    pass
```

### 便捷函数

```python
from src.data.storage.database import execute_query, execute_command, read_sql, save_to_sql

# 直接执行查询
results = execute_query("SELECT * FROM your_table")

# 执行命令
affected = execute_command("UPDATE your_table SET col1 = :val WHERE id = :id",
                          {'val': 'new_value', 'id': 1})

# DataFrame操作
df = read_sql("SELECT * FROM your_table")
save_to_sql(df, 'backup_table')
```

## 功能特性

### 连接池管理

-   自动连接池管理，支持高并发
-   连接超时和重连机制
-   连接健康检查

### 事务支持

-   自动事务管理
-   异常时自动回滚
-   上下文管理器支持

### 日志记录

-   完整的数据库操作日志
-   错误追踪和调试信息
-   分离的数据库日志文件

### 数据类型支持

-   自动创建表结构
-   支持常见数据类型映射
-   pandas DataFrame 集成

## 配置选项

### 连接池配置

在 `config/config.yaml` 中调整连接池参数：

```yaml
database:
    mysql:
        pool:
            pool_size: 10 # 连接池大小
            max_overflow: 20 # 最大溢出连接数
            pool_timeout: 30 # 获取连接超时时间(秒)
            pool_recycle: 3600 # 连接回收时间(秒)
            pool_pre_ping: true # 连接前ping检查
```

### 连接参数

```yaml
database:
    mysql:
        connect_args:
            connect_timeout: 10 # 连接超时时间(秒)
            read_timeout: 30 # 读取超时时间(秒)
            write_timeout: 30 # 写入超时时间(秒)
```

## 常见问题

### 1. 连接失败

**错误信息**: `数据库连接失败`

**解决方案**:

-   检查 MySQL 服务是否启动
-   验证用户名和密码
-   确认数据库是否存在
-   检查防火墙设置

### 2. 权限错误

**错误信息**: `Access denied for user`

**解决方案**:

```sql
-- 授予用户权限
GRANT ALL PRIVILEGES ON marketseer.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 字符集问题

**错误信息**: `Incorrect string value`

**解决方案**:

-   确保数据库使用 utf8mb4 字符集
-   检查配置文件中的 charset 设置

### 4. 连接池耗尽

**错误信息**: `QueuePool limit of size 10 overflow 20 reached`

**解决方案**:

-   增加连接池大小
-   检查是否有未关闭的连接
-   使用上下文管理器确保连接正确释放

## 最佳实践

### 1. 使用事务

```python
with database_session() as session:
    # 所有操作在一个事务中
    session.execute(...)
    session.execute(...)
    # 自动提交或回滚
```

### 2. 错误处理

```python
try:
    db = get_database()
    result = db.execute_query("SELECT * FROM table")
except Exception as e:
    logger.error(f"数据库操作失败: {e}")
    # 处理错误
```

### 3. 资源清理

```python
from src.data.storage.database import close_database

# 应用退出时清理资源
try:
    # 应用逻辑
    pass
finally:
    close_database()
```

### 4. 配置管理

-   敏感信息使用环境变量
-   不同环境使用不同配置文件
-   定期备份配置文件

## 进阶用法

### 自定义数据库操作

```python
from src.data.storage.database import DatabaseManager

class CustomDatabaseManager(DatabaseManager):
    def custom_operation(self):
        # 自定义数据库操作
        pass

# 使用自定义管理器
custom_db = CustomDatabaseManager()
```

### 多数据库支持

```python
# 在config.yaml中配置多个数据库
database:
    mysql_main:
        # 主数据库配置
    mysql_backup:
        # 备份数据库配置

# 使用不同数据库
main_db = DatabaseManager('mysql_main')
backup_db = DatabaseManager('mysql_backup')
```

## 监控和维护

### 连接状态监控

```python
db = get_database()
conn_info = db.get_connection_info()
print(f"连接池状态: {conn_info}")
```

### 日志分析

数据库操作日志位于 `logs/database.log`，包含：

-   连接状态变化
-   SQL 执行记录
-   错误信息
-   性能指标

### 性能优化

1. **连接池调优**: 根据并发量调整连接池大小
2. **索引优化**: 为常用查询添加索引
3. **查询优化**: 使用 EXPLAIN 分析查询性能
4. **定期维护**: 清理日志文件，优化表结构

---

如有问题，请查看日志文件或联系开发团队。
