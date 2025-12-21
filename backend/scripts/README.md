# MarketSeer 数据导入脚本

本目录包含用于数据导入和维护的脚本工具。

---

## range_upsert_daily_dragon_tiger.py

### 概述

`range_upsert_daily_dragon_tiger.py` 是用于将指定日期的龙虎榜数据导入数据库的脚本。

### 功能特点

- ✅ 支持单日数据导入
- ✅ 支持日期范围批量导入
- ✅ 智能去重（使用四字段复合键：code + listed_date + reasons + analysis）
- ✅ 自动创建/更新记录
- ✅ 完整的错误处理和日志记录
- ✅ 详细的导入统计信息

### 使用方法

#### 1. 导入指定日期的龙虎榜数据

```bash
python backend/scripts/range_upsert_daily_dragon_tiger.py --date 20251219
```

**参数说明：**
- `--date`: 指定日期，格式为 YYYYMMDD（例如：20251219 表示 2025年12月19日）

**输出示例：**
```
开始批量导入龙虎榜数据
日期数量: 1
导入日期: 20251219
✓ 龙虎榜数据导入完成: 20251219 - 创建 68 条, 更新 0 条
导入完成
成功: 1 天
失败: 0 天
总计创建: 68 条
总计更新: 0 条
```

#### 2. 导入日期范围的龙虎榜数据

```bash
python backend/scripts/range_upsert_daily_dragon_tiger.py --start-date 20251215 --end-date 20251219
```

**参数说明：**
- `--start-date`: 开始日期，格式为 YYYYMMDD
- `--end-date`: 结束日期，格式为 YYYYMMDD

**说明：**
- 脚本会自动导入指定日期范围内的所有日期（包括起止日期）
- 适合批量补充历史数据

#### 3. 查看帮助信息

```bash
python backend/scripts/range_upsert_daily_dragon_tiger.py --help
```

### 数据去重逻辑

脚本使用 **四字段复合键** 判断记录是否重复：
- `code`: 股票代码
- `listed_date`: 上榜日期
- `reasons`: 上榜原因
- `analysis`: 解读

**特点：**
- 同一股票在同一天因不同原因上榜会被视为**不同记录**
- 完全相同的记录会被更新，而不是重复创建
- 保证数据完整性，不会丢失独立的上榜记录

**示例：**
```
平潭发展(000592) 在 2025-12-19 有 2 条独立记录：
1. 上榜原因：日振幅值达到15%的前5只证券
2. 上榜原因：日跌幅偏离值达到7%的前5只证券
这两条记录会被分别保存，不会相互覆盖
```

### 注意事项

1. **日期格式**：必须使用 YYYYMMDD 格式（8位数字）
2. **数据源**：数据来自 akshare API，需要确保网络连接正常
3. **重复运行**：多次运行相同日期不会产生重复数据，只会更新现有记录
4. **日志文件**：所有操作日志会保存在 `backend/logs/` 目录

### 常见问题

**Q: 如何导入最近一周的数据？**
```bash
python backend/scripts/range_upsert_daily_dragon_tiger.py --start-date 20251213 --end-date 20251219
```

**Q: 如何更新今天的数据？**
```bash
# 使用今天的日期，例如 2025年12月20日
python backend/scripts/range_upsert_daily_dragon_tiger.py --date 20251220
```

**Q: 导入失败怎么办？**
- 检查网络连接
- 查看 `backend/logs/` 目录下的错误日志
- 确认日期格式是否正确

### 技术实现

- **数据映射层**: `app.mapping.dragon_tiger.daily_mapping`
- **业务逻辑层**: `app.services.dragon_tiger_service.DragonTigerService`
- **数据访问层**: `app.repository.dragon_tiger.DailyDragonTigerRepository`
- **数据模型**: `app.models.dragon_tiger.daily_dragon_tiger.DailyDragonTiger`

---

## download_akshare_data.py

### 概述

`download_akshare_data.py` 是用于下载指定 akshare API 数据并保存到本地 JSON 文件的脚本。

### 功能特点

- ✅ 支持任意 akshare API 下载
- ✅ 支持单日数据下载
- ✅ 支持日期范围批量下载
- ✅ 自动保存为 JSON 格式到 `backend/data/akshare_raw/` 目录
- ✅ 完整的错误处理和日志记录
- ✅ 详细的下载统计信息

### 使用方法

#### 1. 下载活跃营业部数据

```bash
python backend/scripts/download_akshare_data.py --api stock_lhb_hyyyb_em --start-date 20251218 --end-date 20251218
```

**参数说明：**
- `--api`: akshare API 名称（如：stock_lhb_hyyyb_em）
- `--start-date`: 开始日期，格式为 YYYYMMDD
- `--end-date`: 结束日期，格式为 YYYYMMDD

**输出示例：**
```
开始批量下载 stock_lhb_hyyyb_em 数据
日期范围: 20251218 - 20251218
日期数量: 1
下载 API: stock_lhb_hyyyb_em, 日期: 20251218
✓ 数据已保存到: C:\Users\Max\Desktop\MarketSeer\backend\data\akshare_raw\stock_lhb_hyyyb_em_20251218_20251218.json
✓ 数据行数: 249
✓ 数据列数: 10
下载完成
成功: 1 天
失败: 0 天
```

#### 2. 下载日期范围数据

```bash
python backend/scripts/download_akshare_data.py --api stock_lhb_hyyyb_em --start-date 20251215 --end-date 20251219
```

**说明：**
- 脚本会为每个日期生成单独的 JSON 文件
- 文件命名格式：`{api_name}_{start_date}_{end_date}.json`

#### 3. 查看帮助信息

```bash
python backend/scripts/download_akshare_data.py --help
```

### 数据格式

- **保存位置**: `backend/data/akshare_raw/` 目录
- **文件格式**: JSON (包含字典列表)
- **文件名格式**: `{API名称}_{开始日期}_{结束日期}.json`

### 注意事项

1. **API 名称**: 必须是有效的 akshare API 函数名
2. **日期格式**: 必须使用 YYYYMMDD 格式（8位数字）
3. **数据类型**: 仅支持返回 pandas DataFrame 的 API
4. **网络连接**: 需要确保网络连接正常
5. **文件覆盖**: 相同参数会覆盖已存在的文件

### 常见问题

**Q: 如何下载其他 akshare 数据？**
```bash
# 例如下载龙虎榜详细数据
python backend/scripts/download_akshare_data.py --api stock_lhb_detail_em --start-date 20251218 --end-date 20251218
```

**Q: 下载失败怎么办？**
- 检查网络连接
- 确认 API 名称是否正确
- 查看控制台错误日志
- 确认日期格式是否正确

### 技术实现

- **数据源**: `app.data_sources.akshare_client.AkshareClient`
- **数据格式**: pandas DataFrame → JSON (字典列表)
- **日志系统**: 集成项目日志系统

---

## 其他脚本

（待添加）
