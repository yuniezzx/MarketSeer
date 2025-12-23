# DragonTiger Analysis（分析与总结）说明文档

> 适用页面：`frontend/src/pages/DragonTiger/index.jsx` -> Tab: **分析与总结**
> 
> 适用组件：`frontend/src/pages/DragonTiger/analysis.jsx`

本分析模块当前聚焦两类数据源：

- **brokerageData**：每日机构榜（按日期分组）
- **rangeData**：范围龙虎榜（按日期+股票聚合 reasons）

---

## 1. 数据流与来源

### 1.1 页面查询入口（index.jsx）
在 `DragonTiger` 页面首次加载、以及点击“查询”按钮时会发起三类请求：

- `getDailyDragonTiger(daysBack)` -> `dragonTigerData`（当前 Analysis 不再使用）
- `getDailyActiveBrokerage(daysBack)` -> `brokerageData`
- `getDragonTigerByRange(startDateFormatted, endDateFormatted)` -> `rawRangeData` -> 过滤 -> `rangeData`

其中 Analysis Tab 传参为：

```jsx
<DragonTigerAnalysis
  brokerageData={brokerageData}
  rangeData={rangeData}
  dateRange={{ startDate, endDate }}
/>
```

### 1.2 工具函数（utils.js）

#### groupDataByDate(data)
- 输入：按记录平铺的数组（每条含 `listed_date`）
- 输出：按日期分组的数组

返回结构：
```js
[
  {
    date: "2025-12-23",
    data: [/* 当天聚合后的记录 */]
  },
  ...
]
```

注意：`groupDataByDate` 内部会调用 `aggregateReasons`，对每个日期内数据进一步聚合。

#### aggregateReasons(data)
- 聚合维度：`listed_date + (code 或 brokerage_code)`
- 将同一 key 的 `reasons` 合并为数组

聚合后：
- `reasons` 字段从字符串变为数组 `string[]`
- 其他字段保持 item 原样

---

## 2. 数据结构定义（前端视角）

> 下面字段来自列定义 `frontend/src/pages/DragonTiger/columns.jsx` 与 utils 聚合逻辑，字段以实际 API 返回为准。

### 2.1 brokerageData（每日机构榜）

类型：
```ts
type BrokerageGroup = {
  date: string; // 例如 "2025-12-23"（来自 listed_date）
  data: BrokerageRecord[];
}

type BrokerageRecord = {
  listed_date: string;
  brokerage_code: string;
  brokerage_name: string;
  buy_stock_count?: number;
  sell_stock_count?: number;
  buy_total_amount?: number;
  sell_total_amount?: number;
  net_total_amount?: number;
  buy_stocks?: string;
  reasons?: string[]; // groupDataByDate 后可能出现（若接口提供 reasons）
}

type brokerageData = BrokerageGroup[]
```

说明：
- `brokerageData.length` 是“日期组”数量
- 真正的记录条数需要累加：`sum(group.data.length)`

### 2.2 rangeData（范围龙虎榜）

rangeData 是由 `getDragonTigerByRange()` 返回的平铺数据，经 `aggregateReasons` 聚合，再经过过滤（ST、涨跌幅、换手率、收盘价）后得到。

类型：
```ts
type RangeRecord = {
  listed_date: string; // YYYYMMDD 或 YYYY-MM-DD（以接口为准）
  code: string;
  name: string;
  close_price?: number;
  change_percent?: number;
  turnover_rate?: number;
  lhb_net_amount?: number;
  lhb_trade_amount?: number;
  reasons: string[]; // 聚合后为数组
}

type rangeData = RangeRecord[]
```

关于“聚合后算几条”：
- 聚合后每条 `RangeRecord` **算 1 条记录**
- 聚合只改变 `reasons` 的形态（字符串 -> 数组），并对同一天同股票去重
- 因此 `rangeData.length` 表示 **聚合后记录数**（而不是聚合前原始总数）

---

## 3. 当前 Analysis 页面展示（现状）

`analysis.jsx` 目前实现：

### 3.1 统计汇总（Summary）
展示一行提示框：

- 券商数据条数：`brokerageData.reduce((sum, g) => sum + g.data.length, 0)`
- 范围数据条数：`rangeData.length`
- 日期区间：`dateRange.startDate - dateRange.endDate`

### 3.2 热点股票 / 趋势分析
目前为占位内容（后续可逐步补齐）。

---

## 4. 可以做哪些分析（建议指标清单）

> 这里是“可做”的方向，用于你后续决定 Analysis 要实现哪些模块。

### 4.1 基于 brokerageData（每日机构榜）

1) **最活跃营业部 TopN（按出现次数）**
- 指标：营业部出现次数（跨天累加记录数）
- 数据：`brokerage_code/brokerage_name`

2) **净买入最强营业部 TopN**
- 指标：按 `net_total_amount` 分组汇总

3) **每日机构活跃度趋势**
- 每天记录数：`group.data.length`
- 每天净买入总额：`sum(net_total_amount)`

4) **买入金额/卖出金额强度**
- 汇总 `buy_total_amount`/`sell_total_amount` 形成排行

5) **席位偏好股票（可选）**
- 解析 `buy_stocks`（若是可解析的字符串格式）统计 TopN


### 4.2 基于 rangeData（范围龙虎榜）

1) **区间热点股票 TopN**
- 指标 A：出现次数（同一天同股票聚合后，出现即+1）
- 指标 B：净买入总额汇总 `lhb_net_amount`

2) **区间上榜原因热度 TopN**
- 将所有 `reasons` flatten，然后计数

3) **资金强度 TopN**
- `lhb_net_amount` 净买入 TopN
- `lhb_trade_amount` 成交额 TopN

4) **涨跌幅/换手率分布**
- 分桶统计（如 <3%、3-7%、7-15%、>15%）

5) **过滤器效果（可选）**
- 需要把 rawRangeDataCount 或 rawRangeData 也传到 Analysis


### 4.3 brokerageData + rangeData 联合分析（更进阶，可选）

1) **资金共振日（重点日识别）**
- 同一天 rangeData 记录数高 + brokerageData 净买入高

2) **趋势相关性（粗略）**
- 按天对齐两条时间序列：机构活跃度 vs 龙虎榜热度

---

## 5. 建议的代码结构（后续实现分析计算）

为了让组件更“展示化”，建议把分析计算抽到一个纯函数文件：

- 推荐文件名：`frontend/src/pages/DragonTiger/helper.jsx`
  - 已存在该文件（当前 repo 里能看到），可在此扩展
- 或新增：`frontend/src/pages/DragonTiger/analysisUtils.js`

建议函数签名：
```js
export function calcBrokerageStats(brokerageData) {}
export function calcRangeStats(rangeData) {}
export function calcReasonTopN(rangeData, topN = 10) {}
```

这样 `analysis.jsx` 只负责：
- 调用 `calc...`
- 把结果渲染成 Card / 图表

---

## 6. 口径说明（避免误解）

- **brokerageData 的“条数”**：推荐口径为“所有日期组内记录总数”，即累加 `group.data.length`。
- **rangeData 的“条数”**：是 `aggregateReasons` 聚合后的记录数（同一天同股票被合并）。
- **reasons 字段**：聚合后为数组，需要展开统计。

---

## 7. 下一步（你可以选择）

你如果告诉我你希望：
- “热点股票”展示 TopN 的口径（按次数还是按净买入）
- “趋势分析”想看哪两个指标（记录数趋势/净买入趋势/原因趋势）

我可以把这些分析计算真正落地到 `helper.jsx`（或新建 utils 文件）并在 UI 中展示。
