import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import MultipleListingChart from "@/components/DragonTiger/MultipleListingChart";
import { getMultipleListingStocks, formatChartData, sortChartData } from "./helper";

function DragonTigerAnalysis({ brokerageData = [], rangeData = [], dateRange = {} }) {
  const [activeAnalysis, setActiveAnalysis] = useState("summary");
  const [sortMode, setSortMode] = useState("count"); // 'count' | 'buy' | 'sell'

  // 统计多次上榜的股票
  const multipleListingStocks = getMultipleListingStocks(rangeData);

  // 格式化全部数据（不限制数量）
  const allChartData = formatChartData(multipleListingStocks);

  // 先根据排序模式排序全部数据，再取前15名
  const sortedData = sortChartData(allChartData, sortMode);
  const chartData = sortedData.slice(0, 15);

  // 排序模式标签
  const sortModeLabels = {
    count: "按上榜次数",
    buy: "按净买入",
    sell: "按净卖出",
  };

  // 切换排序模式
  const handleSortToggle = () => {
    setSortMode(prev => {
      if (prev === "count") return "buy";
      if (prev === "buy") return "sell";
      return "count";
    });
  };

  const renderSummaryStats = () => {
    return (
      <div className="space-y-6">
        {/* 基础统计信息 */}
        <Card>
          <CardHeader>
            <CardTitle>统计汇总</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  📊 券商数据: {brokerageData.reduce((sum, group) => sum + group.data.length, 0)} 条, 范围数据: {rangeData.length}{" "}
                  条, 日期区间: {dateRange.startDate} - {dateRange.endDate}
                </p>
              </div>

              {/* 多次上榜统计卡片 */}
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <h3 className="text-sm font-semibold text-green-800 dark:text-green-200 mb-2">🔥 多次上榜股票统计</h3>
                <p className="text-sm text-green-700 dark:text-green-300">
                  共有 <span className="font-bold text-lg">{multipleListingStocks.length}</span> 只股票在日期区间内上榜超过一次
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 图表与明细表 - 使用标签页切换 */}
        {multipleListingStocks.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>多次上榜股票分析</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="chart" className="w-full">
                <TabsList className="grid w-full grid-cols-2 max-w-md">
                  <TabsTrigger value="chart">📊 资金流向图</TabsTrigger>
                  <TabsTrigger value="table">📋 明细表</TabsTrigger>
                </TabsList>

                <TabsContent value="chart" className="mt-6">
                  <MultipleListingChart
                    data={chartData}
                    sortMode={sortMode}
                    sortModeLabel={sortModeLabels[sortMode]}
                    onSortToggle={handleSortToggle}
                    onBarClick={data => console.log("Clicked:", data)}
                  />
                </TabsContent>

                <TabsContent value="table" className="mt-6">
                  <div className="overflow-auto" style={{ maxHeight: `${Math.max(400, chartData.length * 35)}px` }}>
                    <table className="w-full text-sm">
                      <thead className="bg-gray-100 dark:bg-gray-800">
                        <tr>
                          <th className="px-4 py-2 text-left">排名</th>
                          <th className="px-4 py-2 text-left">股票代码</th>
                          <th className="px-4 py-2 text-left">股票名称</th>
                          <th className="px-4 py-2 text-center">上榜次数</th>
                          <th className="px-4 py-2 text-right">总净买入额(万)</th>
                          <th className="px-4 py-2 text-left">上榜日期</th>
                        </tr>
                      </thead>
                      <tbody>
                        {sortedData.map((stock, index) => (
                          <tr key={stock.code} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                            <td className="px-4 py-2">{index + 1}</td>
                            <td className="px-4 py-2 font-mono">{stock.code}</td>
                            <td className="px-4 py-2">{stock.name}</td>
                            <td className="px-4 py-2 text-center">
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                                {stock.count} 次
                              </span>
                            </td>
                            <td className="px-4 py-2 text-right">
                              <span
                                className={`font-semibold ${
                                  stock.netAmount >= 0 ? "text-red-600 dark:text-red-400" : "text-green-600 dark:text-green-400"
                                }`}
                              >
                                {stock.netAmount >= 0 ? "+" : ""}
                                {stock.netAmount.toFixed(2)}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-xs">
                              <TooltipProvider>
                                <div className="flex flex-wrap gap-1">
                                  {stock.details &&
                                    stock.details.map((detail, idx) => (
                                      <Tooltip key={idx}>
                                        <TooltipTrigger asChild>
                                          <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded cursor-help hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors">
                                            {detail.listed_date || stock.dates[idx]}
                                          </span>
                                        </TooltipTrigger>
                                        <TooltipContent className="max-w-xs">
                                          <div className="text-sm">
                                            <p className="font-semibold mb-1">上榜原因：</p>
                                            {detail.reasons && detail.reasons.length > 0 ? (
                                              <ul className="list-disc list-inside space-y-1">
                                                {detail.reasons.map((reason, ridx) => (
                                                  <li key={ridx} className="text-gray-700 dark:text-gray-300">
                                                    {reason}
                                                  </li>
                                                ))}
                                              </ul>
                                            ) : (
                                              <p className="text-gray-700 dark:text-gray-300">未知原因</p>
                                            )}
                                          </div>
                                        </TooltipContent>
                                      </Tooltip>
                                    ))}
                                </div>
                              </TooltipProvider>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  const renderHotStocks = () => {
    return (
      <Card>
        <CardHeader>
          <CardTitle>热点股票</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">热点股票分析内容</p>
        </CardContent>
      </Card>
    );
  };

  const renderTrends = () => {
    return (
      <Card>
        <CardHeader>
          <CardTitle>趋势分析</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">趋势分析内容</p>
        </CardContent>
      </Card>
    );
  };

  if (brokerageData.length === 0 && rangeData.length === 0) {
    return <div className="p-6 text-center text-gray-500">暂无数据可供分析，请先在其他标签页获取数据</div>;
  }

  return (
    <div className="p-6">
      <div onClick={() => console.log(multipleListingStocks)}>Click</div>
      <div className="mb-6">
        <div className="flex space-x-2 mb-4">
          <button
            onClick={() => setActiveAnalysis("summary")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeAnalysis === "summary"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            }`}
          >
            统计汇总
          </button>
          <button
            onClick={() => setActiveAnalysis("hot-stocks")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeAnalysis === "hot-stocks"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            }`}
          >
            热点股票
          </button>
          <button
            onClick={() => setActiveAnalysis("trends")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeAnalysis === "trends"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            }`}
          >
            趋势分析
          </button>
        </div>
      </div>

      {activeAnalysis === "summary" && renderSummaryStats()}
      {activeAnalysis === "hot-stocks" && renderHotStocks()}
      {activeAnalysis === "trends" && renderTrends()}
    </div>
  );
}

export default DragonTigerAnalysis;
