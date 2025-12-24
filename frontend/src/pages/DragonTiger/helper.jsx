/**
 * 统计日期区间内多次上榜的股票数据
 * @param {Array} rangeData - 原始数据数组
 * @returns {Array} 多次上榜的股票统计数据
 */
export const getMultipleListingStocks = rangeData => {
  const stockMap = new Map();

  rangeData.forEach(item => {
    const code = item.code;
    const name = item.name || "";

    if (!code) return;

    if (!stockMap.has(code)) {
      stockMap.set(code, {
        code,
        name,
        count: 0,
        dates: [],
        totalNetAmount: 0, // 累计净买入额
        totalBuyAmount: 0, // 累计买入总额
        totalSellAmount: 0, // 累计卖出总额
        totalTradeAmount: 0, // 累计成交额
        details: [],
      });
    }

    const stock = stockMap.get(code);
    stock.count += 1;
    stock.dates.push(item.listed_date || "");
    stock.details.push(item);

    // 累加金额数据（单位：元）
    stock.totalNetAmount += item.lhb_net_amount || 0;
    stock.totalBuyAmount += item.lhb_buy_amount || 0;
    stock.totalSellAmount += item.lhb_sell_amount || 0;
    stock.totalTradeAmount += item.lhb_trade_amount || 0;
  });

  // 筛选出现超过一次的股票，并按上榜次数降序排列
  return Array.from(stockMap.values())
    .filter(stock => stock.count > 1)
    .sort((a, b) => b.count - a.count);
};

/**
 * 根据上榜次数返回对应的颜色
 * @param {number} count - 上榜次数
 * @param {boolean} isPositive - 是否为净买入（正值）
 * @returns {string} 颜色代码
 */
export const getColorByCount = (count, isPositive = true) => {
  if (isPositive) {
    // 净买入：红色系（A股习惯）
    if (count >= 6) return "#dc2626"; // 深红
    if (count >= 4) return "#ef4444"; // 中红
    return "#f87171"; // 浅红
  } else {
    // 净卖出：绿色系（A股习惯）
    if (count >= 6) return "#059669"; // 深绿
    if (count >= 4) return "#10b981"; // 中绿
    return "#34d399"; // 浅绿
  }
};

/**
 * 将统计数据转换为图表所需的格式
 * @param {Array} multipleListingStocks - 多次上榜股票数据
 * @param {number} topN - 显示前N名，不传则显示全部
 * @returns {Array} 图表数据
 */
export const formatChartData = (multipleListingStocks, topN) => {
  const dataToFormat = topN ? multipleListingStocks.slice(0, topN) : multipleListingStocks;
  return dataToFormat.map(stock => ({
    name: stock.name,
    code: stock.code,
    fullName: `${stock.name}\n(${stock.code})`,
    count: stock.count,
    netAmount: stock.totalNetAmount / 10000, // 转换为万元
    buyAmount: stock.totalBuyAmount / 10000,
    sellAmount: stock.totalSellAmount / 10000,
    tradeAmount: stock.totalTradeAmount / 10000,
    dates: stock.dates,
    details: stock.details, // 保留详细信息用于显示上榜原因
    isPositive: stock.totalNetAmount >= 0,
    color: getColorByCount(stock.count, stock.totalNetAmount >= 0),
  }));
};

/**
 * 格式化金额显示
 * @param {number} amount - 金额（万元）
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的金额字符串
 */
export const formatAmount = (amount, decimals = 2) => {
  if (amount === null || amount === undefined) return "-";

  const absAmount = Math.abs(amount);
  const sign = amount >= 0 ? "+" : "-";

  if (absAmount >= 10000) {
    // 大于1亿，显示为亿
    return `${sign}${(absAmount / 10000).toFixed(decimals)}亿`;
  }

  // 显示为万
  return `${sign}${absAmount.toFixed(decimals)}万`;
};

/**
 * 格式化日期列表显示
 * @param {Array} dates - 日期数组
 * @returns {string} 格式化后的日期字符串
 */
export const formatDates = dates => {
  if (!dates || dates.length === 0) return "-";
  return dates.join(", ");
};

/**
 * 获取上榜次数的描述
 * @param {number} count - 上榜次数
 * @returns {string} 描述文本
 */
export const getCountDescription = count => {
  if (count >= 6) return "高频上榜";
  if (count >= 4) return "频繁上榜";
  return "多次上榜";
};

/**
 * 对图表数据进行排序
 * @param {Array} data - 图表数据数组
 * @param {string} mode - 排序模式：'count' | 'buy' | 'sell'
 * @returns {Array} 排序后的数据
 */
export const sortChartData = (data, mode) => {
  const sorted = [...data];
  switch (mode) {
    case "count":
      // 按上榜次数降序
      return sorted.sort((a, b) => b.count - a.count);
    case "buy":
      // 按净买入金额降序
      return sorted.sort((a, b) => b.netAmount - a.netAmount);
    case "sell":
      // 按净卖出金额降序（负值绝对值越大越靠前）
      return sorted.sort((a, b) => a.netAmount - b.netAmount);
    default:
      return sorted;
  }
};
