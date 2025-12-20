import { useState } from "react";
import dayjs from "dayjs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getDailyDragonTiger } from "@/api/dragonTiger";

function DragonTiger() {
  // 计算开始日期：前两个星期，但不超过2025/12/01
  const defaultStartDate = dayjs().subtract(14, "days");
  const cutoffDate = dayjs("2025-12-01");
  const startDateValue = defaultStartDate.isBefore(cutoffDate) ? cutoffDate : defaultStartDate;

  const [startDate, setStartDate] = useState(startDateValue.format("YYYY-MM-DD"));
  const [endDate, setEndDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [daysBack, setDaysBack] = useState(7);
  const [loading, setLoading] = useState(false);
  const [dragonTigerData, setDragonTigerData] = useState([]);
  const [error, setError] = useState(null);

  // 查询每日龙虎榜数据
  const handleDailyQuery = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDailyDragonTiger(daysBack);
      if (response.status === "success") {
        // 将数据按日期分组
        const groupedData = groupDataByDate(response.data);
        setDragonTigerData(groupedData);
      } else {
        setError(response.message || "查询失败");
      }
    } catch (err) {
      setError(err.message || "网络请求失败");
    } finally {
      setLoading(false);
    }
  };

  // 将数据按日期分组的函数
  const groupDataByDate = data => {
    const grouped = {};

    data.forEach(item => {
      const date = item.listed_date;
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(item);
    });

    // 转换为数组格式，每个元素是 {日期: 数据列表}
    return Object.keys(grouped)
      .sort((a, b) => b.localeCompare(a)) // 按日期降序排列
      .map(date => ({
        [date]: grouped[date],
      }));
  };

  return (
    <div className="p-6">
      <Tabs defaultValue="daily" className="w-full">
        <TabsList className="w-fit grid grid-cols-3">
          <TabsTrigger value="daily" className="text-sm">
            每日模式
          </TabsTrigger>
          <TabsTrigger value="date-range" className="text-sm">
            日期范围模式
          </TabsTrigger>
          <TabsTrigger value="summary" className="text-sm">
            总表模式
          </TabsTrigger>
        </TabsList>

        <TabsContent value="daily" className="mt-4">
          <div className="p-6 border rounded-lg">
            <div className="flex items-center justify-end gap-2 mb-4">
              <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">今天: {dayjs().format("YYYY-MM-DD")}</span>
              <Input
                type="number"
                value={daysBack}
                onChange={e => setDaysBack(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-20"
                disabled={loading}
                size="sm"
                min="1"
                max="365"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">天</span>
              <Button
                disabled={loading}
                variant="default"
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white border border-blue-600"
                onClick={handleDailyQuery}
              >
                {loading ? "查询中..." : `查询`}
              </Button>
            </div>

            {/* 查询结果区域 */}
            <div>
              {error && (
                <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                </div>
              )}

              {!loading && !error && dragonTigerData.length === 0 && (
                <p className="text-gray-600 dark:text-gray-400 text-sm">设置天数后点击查询按钮查看最近N天的龙虎榜数据</p>
              )}

              {!loading && dragonTigerData.length > 0 && (
                <div className="space-y-6">
                  {dragonTigerData.map((dateGroup, groupIndex) => {
                    const date = Object.keys(dateGroup)[0];
                    const records = dateGroup[date];
                    const totalRecords = dragonTigerData.reduce((sum, group) => sum + Object.values(group)[0].length, 0);

                    return (
                      <div key={groupIndex} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            {date} ({records.length}条记录)
                          </h3>
                          {groupIndex === 0 && (
                            <p className="text-sm text-gray-600 dark:text-gray-400">共查询到 {totalRecords} 条记录</p>
                          )}
                        </div>

                        <div className="border rounded-lg overflow-hidden">
                          <div className="overflow-x-auto">
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead className="w-24 text-center">股票代码</TableHead>
                                  <TableHead className="w-28 text-center">股票名称</TableHead>
                                  <TableHead className="text-center w-24">收盘价</TableHead>
                                  <TableHead className="text-center w-24">涨跌幅(%)</TableHead>
                                  <TableHead className="text-center w-24">换手率(%)</TableHead>
                                  <TableHead className="text-center w-32">龙虎榜净买额(万)</TableHead>
                                  <TableHead className="text-center w-32">龙虎榜成交额(万)</TableHead>
                                  <TableHead className="text-center min-w-48">上榜原因</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {records.map((item, index) => (
                                  <TableRow key={index}>
                                    <TableCell className="font-mono text-center">{item.code}</TableCell>
                                    <TableCell className="text-center">{item.name}</TableCell>
                                    <TableCell className="text-center">{item.close_price?.toFixed(2) || "-"}</TableCell>
                                    <TableCell
                                      className={`text-center font-medium ${
                                        item.change_percent > 0
                                          ? "text-red-600 dark:text-red-400"
                                          : item.change_percent < 0
                                          ? "text-green-600 dark:text-green-400"
                                          : ""
                                      }`}
                                    >
                                      {item.change_percent
                                        ? `${item.change_percent > 0 ? "+" : ""}${item.change_percent.toFixed(2)}`
                                        : "-"}
                                    </TableCell>
                                    <TableCell className="text-center">{item.turnover_rate?.toFixed(2) || "-"}</TableCell>
                                    <TableCell
                                      className={`text-center font-medium ${
                                        item.lhb_net_amount > 0
                                          ? "text-red-600 dark:text-red-400"
                                          : item.lhb_net_amount < 0
                                          ? "text-green-600 dark:text-green-400"
                                          : ""
                                      }`}
                                    >
                                      {item.lhb_net_amount ? (item.lhb_net_amount / 10000).toFixed(2) : "-"}
                                    </TableCell>
                                    <TableCell className="text-center">
                                      {item.lhb_trade_amount ? (item.lhb_trade_amount / 10000).toFixed(2) : "-"}
                                    </TableCell>
                                    <TableCell className="text-sm text-center">{item.reasons || "-"}</TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="date-range" className="mt-4">
          <div className="p-6 border rounded-lg">
            <div className="flex items-end gap-4 flex-wrap mb-4">
              <div className="space-x-1">
                <label className="text-sm font-medium">开始日期</label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={e => setStartDate(e.target.value)}
                  className="w-40"
                  disabled={loading}
                  size="sm"
                />
              </div>
              <div className="space-x-1">
                <label className="text-sm font-medium">结束日期</label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={e => setEndDate(e.target.value)}
                  className="w-40"
                  disabled={loading}
                  size="sm"
                />
              </div>
              <Button
                disabled={loading}
                variant="default"
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white border border-blue-600"
              >
                {loading ? "查询中..." : "查询"}
              </Button>
            </div>

            {/* 查询结果区域 */}
            <div className="pt-4">
              <p className="text-gray-600 dark:text-gray-400 text-sm">选择日期范围后点击查询按钮查看龙虎榜数据</p>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="summary" className="mt-4">
          <div className="p-6 border rounded-lg">
            <p className="text-gray-600 dark:text-gray-400 text-sm">在这里显示汇总数据的表格</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default DragonTiger;
