import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from "recharts";
import CustomTooltip from "./CustomTooltip";

/**
 * 多次上榜股票双向柱状图组件
 */
const MultipleListingChart = ({ data, sortMode, sortModeLabel, onSortToggle, onBarClick }) => {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">暂无多次上榜的股票数据</div>;
  }

  // 自定义柱子标签组件 - 显示上榜次数
  const CustomLabel = props => {
    const { x, y, width, value, index } = props;
    const item = data[index];
    const isPositive = item.isPositive;

    // 标签位置计算
    // 正值：x是柱子起点（中轴），width是正数，标签在右侧
    // 负值：x是柱子终点（中轴），width是负数，标签在左侧
    const labelX = isPositive ? x + width + 5 : x + width - 5;
    const textAnchor = isPositive ? "start" : "end";

    return (
      <text x={labelX} y={y + 10} fill={item.color} fontSize={11} fontWeight="bold" textAnchor={textAnchor}>
        {item.count}次
      </text>
    );
  };

  // 格式化Y轴标签（股票名称）
  const formatYAxisLabel = value => {
    const item = data.find(d => d.name === value);
    if (!item) return value;
    // 限制长度，避免过长
    const displayName = item.name.length > 6 ? `${item.name.slice(0, 6)}...` : item.name;
    return displayName;
  };

  // 格式化X轴标签（金额）
  const formatXAxisLabel = value => {
    const absValue = Math.abs(value);
    if (absValue >= 10000) {
      return `${(absValue / 10000).toFixed(1)}亿`;
    }
    return `${absValue.toFixed(0)}万`;
  };

  // 计算X轴的范围
  const maxAbsValue = Math.max(...data.map(d => Math.abs(d.netAmount)));
  const xAxisDomain = [-maxAbsValue * 1.15, maxAbsValue * 1.15]; // 留15%空间给标签

  return (
    <div className="w-full">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">多次上榜股票资金流向</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            双向柱状图：左侧绿色为总净卖出，右侧红色为总净买入 | 柱子颜色深浅表示上榜频率
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onSortToggle}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors border border-gray-300 dark:border-gray-600"
            title="点击切换排序方式"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
              />
            </svg>
            <span>{sortModeLabel}</span>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <div className="text-xs text-gray-500 dark:text-gray-400">显示前 {data.length} 名</div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={Math.max(400, data.length * 35)}>
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 60, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
          <XAxis type="number" domain={xAxisDomain} tickFormatter={formatXAxisLabel} stroke="#9ca3af" fontSize={11} />
          <YAxis type="category" dataKey="name" tickFormatter={formatYAxisLabel} stroke="#9ca3af" fontSize={11} width={80} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(156, 163, 175, 0.1)" }} />
          <Bar dataKey="netAmount" onClick={onBarClick} radius={[0, 4, 4, 0]} cursor="pointer">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
            <LabelList content={<CustomLabel />} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* 图例说明 */}
      <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-600 dark:text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: "#f87171" }}></div>
          <span>浅红：2-3次上榜（净买入）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: "#ef4444" }}></div>
          <span>中红：4-5次上榜（净买入）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: "#dc2626" }}></div>
          <span>深红：6次+上榜（净买入）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: "#34d399" }}></div>
          <span>浅绿：2-3次上榜（净卖出）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: "#10b981" }}></div>
          <span>中绿：4-5次上榜（净卖出）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: "#059669" }}></div>
          <span>深绿：6次+上榜（净卖出）</span>
        </div>
      </div>
    </div>
  );
};

export default MultipleListingChart;
