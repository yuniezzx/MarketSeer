import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";
import { getTurnoverRateColor } from "@/lib/utils";

// 渲染排序图标的函数
const renderSortIcon = column => {
  const isSorted = column.getIsSorted();

  if (isSorted === "asc") {
    return <ChevronUp className="inline w-4 h-4 ml-1 text-blue-600" />;
  } else if (isSorted === "desc") {
    return <ChevronDown className="inline w-4 h-4 ml-1 text-blue-600" />;
  } else {
    return <ChevronsUpDown className="inline w-4 h-4 ml-1 opacity-50" />;
  }
};

// 创建可排序的表头组件
const SortableHeader = ({ column, label }) => {
  return (
    <div
      className="text-center cursor-pointer hover:bg-muted-50 select-none"
      onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
    >
      {label}
      {renderSortIcon(column)}
    </div>
  );
};

// Daily Model 列定义（不含日期列）
export const dailyColumns = [
  {
    accessorKey: "code",
    header: "股票代码",
    cell: ({ row }) => <div className="font-mono text-center">{row.original.code}</div>,
    meta: {
      displayName: "代码",
    },
    enableHiding: false, // 代码列不允许隐藏
  },
  {
    accessorKey: "name",
    header: "股票名称",
    cell: ({ row }) => <div className="text-center">{row.original.name}</div>,
    meta: {
      displayName: "名称",
    },
    enableHiding: false, // 名称列不允许隐藏
  },
  {
    accessorKey: "close_price",
    header: ({ column }) => <SortableHeader column={column} label="收盘价" />,
    cell: ({ row }) => <div className="text-center">{row.original.close_price?.toFixed(2) || "-"}</div>,
    meta: {
      displayName: "收盘价",
    },
  },
  {
    accessorKey: "change_percent",
    header: ({ column }) => <SortableHeader column={column} label="涨跌幅(%)" />,
    cell: ({ row }) => {
      const value = row.original.change_percent;
      return (
        <div
          className={`text-center font-medium ${
            value > 0 ? "text-red-600 dark:text-red-400" : value < 0 ? "text-green-600 dark:text-green-400" : ""
          }`}
        >
          {value ? `${value > 0 ? "+" : ""}${value.toFixed(2)}` : "-"}
        </div>
      );
    },
    meta: {
      displayName: "涨跌幅",
    },
  },
  {
    accessorKey: "turnover_rate",
    header: ({ column }) => <SortableHeader column={column} label="换手率(%)" />,
    cell: ({ row }) => {
      const value = row.original.turnover_rate;
      return <div className={`text-center ${getTurnoverRateColor(value)}`}>{value?.toFixed(2) || "-"}</div>;
    },
    meta: {
      displayName: "换手率",
    },
  },
  {
    accessorKey: "lhb_net_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜净买额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_net_amount;
      return (
        <div
          className={`text-center font-medium ${
            value > 0 ? "text-red-600 dark:text-red-400" : value < 0 ? "text-green-600 dark:text-green-400" : ""
          }`}
        >
          {value ? (value / 10000).toFixed(2) : "-"}
        </div>
      );
    },
    meta: {
      displayName: "净买额",
    },
  },
  {
    accessorKey: "lhb_trade_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜成交额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_trade_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "成交额",
    },
  },
  {
    accessorKey: "lhb_buy_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜买入额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_buy_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "买入额",
    },
  },
  {
    accessorKey: "lhb_sell_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜卖出额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_sell_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "卖出额",
    },
  },
  {
    accessorKey: "circulating_market_cap",
    header: ({ column }) => <SortableHeader column={column} label="流通市值(亿)" />,
    cell: ({ row }) => {
      const value = row.original.circulating_market_cap;
      return <div className="text-center">{value ? (value / 100000000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "流通市值",
    },
  },
  {
    accessorKey: "market_total_amount",
    header: ({ column }) => <SortableHeader column={column} label="市场总成交额(万)" />,
    cell: ({ row }) => {
      const value = row.original.market_total_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "市场总成交额",
    },
  },
  {
    accessorKey: "lhb_net_ratio",
    header: ({ column }) => <SortableHeader column={column} label="净买额占比(%)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_net_ratio;
      return (
        <div
          className={`text-center font-medium ${
            value > 0 ? "text-red-600 dark:text-red-400" : value < 0 ? "text-green-600 dark:text-green-400" : ""
          }`}
        >
          {value ? `${value > 0 ? "+" : ""}${value.toFixed(2)}` : "-"}
        </div>
      );
    },
    meta: {
      displayName: "净买额占比",
    },
  },
  {
    accessorKey: "lhb_trade_ratio",
    header: ({ column }) => <SortableHeader column={column} label="成交额占比(%)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_trade_ratio;
      return <div className="text-center">{value ? value.toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "成交额占比",
    },
  },
  {
    accessorKey: "reasons",
    header: () => <div className="text-center">上榜原因</div>,
    cell: ({ row }) => {
      const reasons = row.original.reasons;
      if (Array.isArray(reasons) && reasons.length > 0) {
        return (
          <div className="text-sm text-center">
            {reasons.map((reason, idx) => (
              <div key={idx} className={idx > 0 ? "mt-1 pt-1 border-t border-gray-200 dark:border-gray-700" : ""}>
                {reason || "-"}
              </div>
            ))}
          </div>
        );
      }
      return <div className="text-sm text-center">{reasons || "-"}</div>;
    },
    meta: {
      displayName: "上榜原因",
    },
    enableHiding: false, // 上榜原因不允许隐藏
  },
];

// 每日活跃营业部列定义
export const brokerageColumns = [
  {
    accessorKey: "brokerage_code",
    header: () => <div className="text-center">营业部代码</div>,
    cell: ({ row }) => <div className="font-mono text-center">{row.original.brokerage_code}</div>,
    meta: {
      displayName: "代码",
    },
    enableHiding: false, // 代码列不允许隐藏
  },
  {
    accessorKey: "brokerage_name",
    header: () => <div className="text-center">营业部名称</div>,
    cell: ({ row }) => <div className="text-center">{row.original.brokerage_name}</div>,
    meta: {
      displayName: "名称",
    },
    enableHiding: false, // 名称列不允许隐藏
  },
  {
    accessorKey: "buy_stock_count",
    header: ({ column }) => <SortableHeader column={column} label="买入个股数" />,
    cell: ({ row }) => <div className="text-center">{row.original.buy_stock_count || "-"}</div>,
    meta: {
      displayName: "买入个股数",
    },
  },
  {
    accessorKey: "sell_stock_count",
    header: ({ column }) => <SortableHeader column={column} label="卖出个股数" />,
    cell: ({ row }) => <div className="text-center">{row.original.sell_stock_count || "-"}</div>,
    meta: {
      displayName: "卖出个股数",
    },
  },
  {
    accessorKey: "buy_total_amount",
    header: ({ column }) => <SortableHeader column={column} label="买入总金额(万)" />,
    cell: ({ row }) => {
      const value = row.original.buy_total_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "买入总金额",
    },
  },
  {
    accessorKey: "sell_total_amount",
    header: ({ column }) => <SortableHeader column={column} label="卖出总金额(万)" />,
    cell: ({ row }) => {
      const value = row.original.sell_total_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "卖出总金额",
    },
  },
  {
    accessorKey: "net_total_amount",
    header: ({ column }) => <SortableHeader column={column} label="总买卖净额(万)" />,
    cell: ({ row }) => {
      const value = row.original.net_total_amount;
      return (
        <div
          className={`text-center font-medium ${
            value > 0 ? "text-red-600 dark:text-red-400" : value < 0 ? "text-green-600 dark:text-green-400" : ""
          }`}
        >
          {value ? (value / 10000).toFixed(2) : "-"}
        </div>
      );
    },
    meta: {
      displayName: "净买额",
    },
  },
  {
    accessorKey: "buy_stocks",
    header: () => <div className="text-center">买入股票</div>,
    cell: ({ row }) => {
      const stocks = row.original.buy_stocks;
      return <div className="text-sm text-center">{stocks || "-"}</div>;
    },
    meta: {
      displayName: "买入股票",
    },
  },
];

// Range Model 列定义（包含日期列）
export const rangeColumns = [
  {
    accessorKey: "listed_date",
    header: ({ column }) => <SortableHeader column={column} label="日期" />,
    cell: ({ row }) => <div className="text-center">{row.original.listed_date}</div>,
    meta: {
      displayName: "日期",
    },
    enableHiding: false, // 日期列不允许隐藏
  },
  {
    accessorKey: "code",
    header: "股票代码",
    cell: ({ row }) => <div className="font-mono text-center">{row.original.code}</div>,
    meta: {
      displayName: "代码",
    },
    enableHiding: false, // 代码列不允许隐藏
  },
  {
    accessorKey: "name",
    header: "股票名称",
    cell: ({ row }) => <div className="text-center">{row.original.name}</div>,
    meta: {
      displayName: "名称",
    },
    enableHiding: false, // 名称列不允许隐藏
  },
  {
    accessorKey: "close_price",
    header: ({ column }) => <SortableHeader column={column} label="收盘价" />,
    cell: ({ row }) => <div className="text-center">{row.original.close_price?.toFixed(2) || "-"}</div>,
    meta: {
      displayName: "收盘价",
    },
  },
  {
    accessorKey: "change_percent",
    header: ({ column }) => <SortableHeader column={column} label="涨跌幅(%)" />,
    cell: ({ row }) => {
      const value = row.original.change_percent;
      return (
        <div
          className={`text-center font-medium ${
            value > 0 ? "text-red-600 dark:text-red-400" : value < 0 ? "text-green-600 dark:text-green-400" : ""
          }`}
        >
          {value ? `${value > 0 ? "+" : ""}${value.toFixed(2)}` : "-"}
        </div>
      );
    },
    meta: {
      displayName: "涨跌幅",
    },
  },
  {
    accessorKey: "turnover_rate",
    header: ({ column }) => <SortableHeader column={column} label="换手率(%)" />,
    cell: ({ row }) => {
      const value = row.original.turnover_rate;
      return <div className={`text-center ${getTurnoverRateColor(value)}`}>{value?.toFixed(2) || "-"}</div>;
    },
    meta: {
      displayName: "换手率",
    },
  },
  {
    accessorKey: "lhb_net_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜净买额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_net_amount;
      return (
        <div
          className={`text-center font-medium ${
            value > 0 ? "text-red-600 dark:text-red-400" : value < 0 ? "text-green-600 dark:text-green-400" : ""
          }`}
        >
          {value ? (value / 10000).toFixed(2) : "-"}
        </div>
      );
    },
    meta: {
      displayName: "净买额",
    },
  },
  {
    accessorKey: "lhb_trade_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜成交额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_trade_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "成交额",
    },
  },
  {
    accessorKey: "lhb_buy_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜买入额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_buy_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "买入额",
    },
  },
  {
    accessorKey: "lhb_sell_amount",
    header: ({ column }) => <SortableHeader column={column} label="龙虎榜卖出额(万)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_sell_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "卖出额",
    },
  },
  {
    accessorKey: "circulating_market_cap",
    header: ({ column }) => <SortableHeader column={column} label="流通市值(亿)" />,
    cell: ({ row }) => {
      const value = row.original.circulating_market_cap;
      return <div className="text-center">{value ? (value / 100000000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "流通市值",
    },
  },
  {
    accessorKey: "market_total_amount",
    header: ({ column }) => <SortableHeader column={column} label="市场总成交额(万)" />,
    cell: ({ row }) => {
      const value = row.original.market_total_amount;
      return <div className="text-center">{value ? (value / 10000).toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "市场总成交额",
    },
  },
  {
    accessorKey: "lhb_net_ratio",
    header: ({ column }) => <SortableHeader column={column} label="净买额占比(%)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_net_ratio;
      return (
        <div
          className={`text-center font-medium ${
            value > 0 ? "text-red-600 dark:text-red-400" : value < 0 ? "text-green-600 dark:text-green-400" : ""
          }`}
        >
          {value ? `${value > 0 ? "+" : ""}${value.toFixed(2)}` : "-"}
        </div>
      );
    },
    meta: {
      displayName: "净买额占比",
    },
  },
  {
    accessorKey: "lhb_trade_ratio",
    header: ({ column }) => <SortableHeader column={column} label="成交额占比(%)" />,
    cell: ({ row }) => {
      const value = row.original.lhb_trade_ratio;
      return <div className="text-center">{value ? value.toFixed(2) : "-"}</div>;
    },
    meta: {
      displayName: "成交额占比",
    },
  },
  {
    accessorKey: "reasons",
    header: () => <div className="text-center">上榜原因</div>,
    cell: ({ row }) => {
      const reasons = row.original.reasons;
      if (Array.isArray(reasons) && reasons.length > 0) {
        return (
          <div className="text-sm text-center">
            {reasons.map((reason, idx) => (
              <div key={idx} className={idx > 0 ? "mt-1 pt-1 border-t border-gray-200 dark:border-gray-700" : ""}>
                {reason || "-"}
              </div>
            ))}
          </div>
        );
      }
      return <div className="text-sm text-center">{reasons || "-"}</div>;
    },
    meta: {
      displayName: "上榜原因",
    },
    enableHiding: false, // 上榜原因不允许隐藏
  },
];
