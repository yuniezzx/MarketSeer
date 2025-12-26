import { formatAmount, formatDates, getCountDescription } from "@/pages/DragonTiger/helper";

/**
 * 自定义图表悬停提示框组件
 */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4 min-w-[280px]">
      {/* 标题 */}
      <div className="border-b border-gray-200 dark:border-gray-700 pb-2 mb-3">
        <h3 className="font-bold text-base text-gray-900 dark:text-gray-100">{data.name}</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 font-mono">{data.code}</p>
      </div>

      {/* 核心指标 */}
      <div className="space-y-2 mb-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-300">📊 上榜次数:</span>
          <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
            {data.count} 次<span className="ml-2 text-xs text-gray-500">({getCountDescription(data.count)})</span>
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-300">💰 净买入额:</span>
          <span
            className={`text-sm font-bold ${
              data.isPositive ? "text-red-600 dark:text-red-400" : "text-green-600 dark:text-green-400"
            }`}
          >
            {formatAmount(data.netAmount)}
          </span>
        </div>
      </div>

      {/* 详细金额 */}
      <div className="bg-gray-50 dark:bg-gray-900 rounded p-2 space-y-1.5 mb-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600 dark:text-gray-400">📈 买入总额:</span>
          <span className="font-semibold text-red-700 dark:text-red-300">{formatAmount(data.buyAmount)}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600 dark:text-gray-400">📉 卖出总额:</span>
          <span className="font-semibold text-green-700 dark:text-green-300">{formatAmount(Math.abs(data.sellAmount))}</span>
        </div>
        <div className="flex items-center justify-between text-xs pt-1 border-t border-gray-200 dark:border-gray-700">
          <span className="text-gray-600 dark:text-gray-400">💵 成交总额:</span>
          <span className="font-semibold text-gray-700 dark:text-gray-300">{formatAmount(data.tradeAmount)}</span>
        </div>
      </div>

      {/* 占比指标 */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded p-2 space-y-1.5 mb-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600 dark:text-gray-400">📊 平均净买额占比:</span>
          <span
            className={`font-semibold ${
              data.avgNetRatio >= 0 ? "text-red-700 dark:text-red-300" : "text-green-700 dark:text-green-300"
            }`}
          >
            {data.avgNetRatio >= 0 ? "+" : ""}
            {data.avgNetRatio?.toFixed(2) || "0.00"}%
          </span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600 dark:text-gray-400">📈 平均成交额占比:</span>
          <span className="font-semibold text-gray-700 dark:text-gray-300">{data.avgTradeRatio?.toFixed(2) || "0.00"}%</span>
        </div>
      </div>

      {/* 上榜日期 */}
      <div className="border-t border-gray-200 dark:border-gray-700 pt-2">
        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1.5">📅 上榜日期:</p>
        <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto">
          {data.dates.map((date, idx) => (
            <span
              key={idx}
              className="text-[10px] px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded"
            >
              {date}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CustomTooltip;
