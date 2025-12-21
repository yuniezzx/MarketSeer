import { useState, useEffect } from "react";
import dayjs from "dayjs";
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getDailyDragonTiger, getDragonTigerByRange } from "@/api/dragonTiger";
import { getTurnoverRateColor } from "@/lib/utils";

function DragonTiger() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 计算开始日期：前一个星期，但不超过2025/12/01
  const defaultStartDate = dayjs().subtract(7, "days");
  const cutoffDate = dayjs("2025-12-01");
  const startDateValue = defaultStartDate.isBefore(cutoffDate) ? cutoffDate : defaultStartDate;

  // ===== 日期和时间相关状态 =====
  const [startDate, setStartDate] = useState(startDateValue.format("YYYY-MM-DD"));
  const [endDate, setEndDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [daysBack, setDaysBack] = useState(7);

  // 每日模式数据
  const [dragonTigerData, setDragonTigerData] = useState([]);

  // 日期范围模式数据
  const [rawRangeData, setRawRangeData] = useState([]); // 存储原始数据
  const [rangeData, setRangeData] = useState([]);
  const [filterOptions, setFilterOptions] = useState({
    excludeST: false, // 排除ST股票
    changePercentMin: "", // 涨跌幅最小值
    changePercentMax: "", // 涨跌幅最大值
    turnoverRateMin: "", // 换手率最小值
    turnoverRateMax: "", // 换手率最大值
  });
  const [sortField, setSortField] = useState(null); // 排序字段
  const [sortDirection, setSortDirection] = useState(null); // 'asc' | 'desc' | null

  // 页面首次加载时自动获取股票
  useEffect(() => {
    handleDailyQuery();
    handleRangeQuery();
  }, []);

  // 监听原始数据、过滤选项和排序状态变化，生成显示数据
  useEffect(() => {
    if (rawRangeData.length > 0) {
      const processedData = generateDisplayedRangeData(rawRangeData, filterOptions);
      setRangeData(processedData);
    } else {
      setRangeData([]);
    }
  }, [rawRangeData, filterOptions, sortField, sortDirection]);

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

  // 查询日期范围的龙虎榜数据
  const handleRangeQuery = async () => {
    setLoading(true);
    setError(null);
    try {
      // 将日期格式从 YYYY-MM-DD 转换为 YYYYMMDD
      const startDateFormatted = startDate.replace(/-/g, "");
      const endDateFormatted = endDate.replace(/-/g, "");

      const response = await getDragonTigerByRange(startDateFormatted, endDateFormatted);
      if (response.status === "success") {
        setRawRangeData(response.data);
      } else {
        setError(response.message || "查询失败");
      }
    } catch (err) {
      setError(err.message || "网络请求失败");
    } finally {
      setLoading(false);
    }
  };

  // 处理日期范围数据以支持单元格合并
  const processRangeDataForMerging = data => {
    // 按日期+代码+名称分组
    const grouped = {};

    data.forEach(item => {
      const key = `${item.listed_date}_${item.code}_${item.name}`;
      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(item);
    });

    // 转换为带有 rowSpan 信息的数组
    const processedData = [];
    Object.values(grouped).forEach(group => {
      group.forEach((item, index) => {
        processedData.push({
          ...item,
          rowSpan: index === 0 ? group.length : 0, // 第一行设置 rowSpan，其他行设置为 0 表示跳过
        });
      });
    });

    return processedData;
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

  // 过滤股票数据的函数
  const filterStocks = (stocks, options) => {
    return stocks.filter(stock => {
      // 排除ST股票
      if (options.excludeST && stock.name.startsWith("*ST")) {
        return false;
      }

      // 涨跌幅区间过滤
      const changePercentMin = options.changePercentMin ? parseFloat(options.changePercentMin) : null;
      const changePercentMax = options.changePercentMax ? parseFloat(options.changePercentMax) : null;

      if (changePercentMin !== null && stock.change_percent < changePercentMin) {
        return false;
      }
      if (changePercentMax !== null && stock.change_percent > changePercentMax) {
        return false;
      }

      // 换手率区间过滤
      const turnoverRateMin = options.turnoverRateMin ? parseFloat(options.turnoverRateMin) : null;
      const turnoverRateMax = options.turnoverRateMax ? parseFloat(options.turnoverRateMax) : null;

      if (turnoverRateMin !== null && stock.turnover_rate < turnoverRateMin) {
        return false;
      }
      if (turnoverRateMax !== null && stock.turnover_rate > turnoverRateMax) {
        return false;
      }

      return true;
    });
  };

  // 排序处理函数
  const handleSort = field => {
    if (sortField === field) {
      // 如果点击的是当前排序字段，则循环：asc -> desc -> null
      if (sortDirection === "asc") {
        setSortDirection("desc");
      } else if (sortDirection === "desc") {
        setSortDirection(null);
      } else {
        setSortDirection("asc");
      }
    } else {
      // 如果点击的是新字段，则设置为升序
      setSortField(field);
      setSortDirection("asc");
    }
  };

  // 排序函数
  const sortData = (data, field, direction) => {
    if (!field || !direction) return data;

    return [...data].sort((a, b) => {
      let valueA, valueB;

      switch (field) {
        case "listed_date":
          valueA = a.listed_date;
          valueB = b.listed_date;
          break;
        case "close_price":
          valueA = a.close_price || 0;
          valueB = b.close_price || 0;
          break;
        case "change_percent":
          valueA = a.change_percent || 0;
          valueB = b.change_percent || 0;
          break;
        case "turnover_rate":
          valueA = a.turnover_rate || 0;
          valueB = b.turnover_rate || 0;
          break;
        case "lhb_net_amount":
          valueA = a.lhb_net_amount || 0;
          valueB = b.lhb_net_amount || 0;
          break;
        case "lhb_trade_amount":
          valueA = a.lhb_trade_amount || 0;
          valueB = b.lhb_trade_amount || 0;
          break;
        default:
          return 0;
      }

      if (direction === "asc") {
        return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
      } else {
        return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
      }
    });
  };

  // 渲染排序图标的函数
  const renderSortIcon = field => {
    if (sortField !== field) {
      // 默认状态：显示双向箭头
      return <ChevronsUpDown className="inline w-4 h-4 ml-1 opacity-50" />;
    }

    // 根据排序方向显示对应图标
    return sortDirection === "asc" ? (
      <ChevronUp className="inline w-4 h-4 ml-1 text-blue-600" />
    ) : sortDirection === "desc" ? (
      <ChevronDown className="inline w-4 h-4 ml-1 text-blue-600" />
    ) : (
      <ChevronsUpDown className="inline w-4 h-4 ml-1 opacity-50" />
    );
  };

  // 生成显示数据的函数
  const generateDisplayedRangeData = (rawData, options) => {
    const filteredData = filterStocks(rawData, options);
    const sortedData = sortData(filteredData, sortField, sortDirection);
    return processRangeDataForMerging(sortedData);
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
          <div className="p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
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
                                    <TableCell className={`text-center ${getTurnoverRateColor(item.turnover_rate)}`}>
                                      {item.turnover_rate?.toFixed(2) || "-"}
                                    </TableCell>
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
          <div className="p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <div className="mb-4">
              <div className="flex items-center justify-end gap-4 mb-2">
                <div className="flex items-center gap-4">
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
                </div>
                <Button
                  disabled={loading}
                  variant="default"
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700 text-white border border-blue-600"
                  onClick={handleRangeQuery}
                >
                  {loading ? "查询中..." : "查询"}
                </Button>
              </div>
              <div className="flex items-center gap-6 p-2 bg-gray-100 dark:bg-gray-700 rounded">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={filterOptions.excludeST}
                    onChange={e => setFilterOptions(prev => ({ ...prev, excludeST: e.target.checked }))}
                    className="rounded"
                  />
                  排除ST股票
                </label>
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium">涨跌幅(%):</label>
                  <Input
                    type="number"
                    placeholder="最小值"
                    value={filterOptions.changePercentMin}
                    onChange={e => setFilterOptions(prev => ({ ...prev, changePercentMin: e.target.value }))}
                    className="w-20"
                    step="0.01"
                    size="sm"
                  />
                  <span className="text-sm text-gray-500">-</span>
                  <Input
                    type="number"
                    placeholder="最大值"
                    value={filterOptions.changePercentMax}
                    onChange={e => setFilterOptions(prev => ({ ...prev, changePercentMax: e.target.value }))}
                    className="w-20"
                    step="0.01"
                    size="sm"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium">换手率(%):</label>
                  <Input
                    type="number"
                    placeholder="最小值"
                    value={filterOptions.turnoverRateMin}
                    onChange={e => setFilterOptions(prev => ({ ...prev, turnoverRateMin: e.target.value }))}
                    className="w-20"
                    step="0.01"
                    size="sm"
                  />
                  <span className="text-sm text-gray-500">-</span>
                  <Input
                    type="number"
                    placeholder="最大值"
                    value={filterOptions.turnoverRateMax}
                    onChange={e => setFilterOptions(prev => ({ ...prev, turnoverRateMax: e.target.value }))}
                    className="w-20"
                    step="0.01"
                    size="sm"
                  />
                </div>
              </div>
            </div>

            {/* 查询结果区域 */}
            <div className="pt-4">
              {error && (
                <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                </div>
              )}

              {!loading && !error && rangeData.length === 0 && (
                <p className="text-gray-600 dark:text-gray-400 text-sm">选择日期范围后点击查询按钮查看龙虎榜数据</p>
              )}

              {!loading && rangeData.length > 0 && (
                <div className="space-y-4">
                  <p className="text-sm text-gray-600 dark:text-gray-400">共查询到 {rangeData.length} 条记录</p>

                  <div className="border rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead
                              className="w-28 text-center cursor-pointer hover:bg-muted-50 select-none"
                              onClick={() => handleSort("listed_date")}
                            >
                              日期{renderSortIcon("listed_date")}
                            </TableHead>
                            <TableHead className="w-24 text-center">股票代码</TableHead>
                            <TableHead className="w-28 text-center">股票名称</TableHead>
                            <TableHead
                              className="text-center w-24 cursor-pointer hover:bg-muted-50 select-none"
                              onClick={() => handleSort("close_price")}
                            >
                              收盘价{renderSortIcon("close_price")}
                            </TableHead>
                            <TableHead
                              className="text-center w-24 cursor-pointer hover:bg-muted-50 select-none"
                              onClick={() => handleSort("change_percent")}
                            >
                              涨跌幅(%){renderSortIcon("change_percent")}
                            </TableHead>
                            <TableHead
                              className="text-center w-24 cursor-pointer hover:bg-muted-50 select-none"
                              onClick={() => handleSort("turnover_rate")}
                            >
                              换手率(%){renderSortIcon("turnover_rate")}
                            </TableHead>
                            <TableHead
                              className="text-center w-32 cursor-pointer hover:bg-muted-50 select-none"
                              onClick={() => handleSort("lhb_net_amount")}
                            >
                              龙虎榜净买额(万){renderSortIcon("lhb_net_amount")}
                            </TableHead>
                            <TableHead
                              className="text-center w-32 cursor-pointer hover:bg-muted-50 select-none"
                              onClick={() => handleSort("lhb_trade_amount")}
                            >
                              龙虎榜成交额(万){renderSortIcon("lhb_trade_amount")}
                            </TableHead>
                            <TableHead className="text-center min-w-48">上榜原因</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {rangeData.map((item, index) => (
                            <TableRow key={index}>
                              {/* 只在第一行显示合并的单元格 */}
                              {item.rowSpan > 0 ? (
                                <>
                                  <TableCell className="text-center" rowSpan={item.rowSpan}>
                                    {item.listed_date}
                                  </TableCell>
                                  <TableCell className="font-mono text-center" rowSpan={item.rowSpan}>
                                    {item.code}
                                  </TableCell>
                                  <TableCell className="text-center" rowSpan={item.rowSpan}>
                                    {item.name}
                                  </TableCell>
                                  <TableCell className="text-center" rowSpan={item.rowSpan}>
                                    {item.close_price?.toFixed(2) || "-"}
                                  </TableCell>
                                  <TableCell
                                    className={`text-center font-medium ${
                                      item.change_percent > 0
                                        ? "text-red-600 dark:text-red-400"
                                        : item.change_percent < 0
                                        ? "text-green-600 dark:text-green-400"
                                        : ""
                                    }`}
                                    rowSpan={item.rowSpan}
                                  >
                                    {item.change_percent
                                      ? `${item.change_percent > 0 ? "+" : ""}${item.change_percent.toFixed(2)}`
                                      : "-"}
                                  </TableCell>
                                  <TableCell
                                    className={`text-center ${getTurnoverRateColor(item.turnover_rate)}`}
                                    rowSpan={item.rowSpan}
                                  >
                                    {item.turnover_rate?.toFixed(2) || "-"}
                                  </TableCell>
                                  <TableCell
                                    className={`text-center font-medium ${
                                      item.lhb_net_amount > 0
                                        ? "text-red-600 dark:text-red-400"
                                        : item.lhb_net_amount < 0
                                        ? "text-green-600 dark:text-green-400"
                                        : ""
                                    }`}
                                    rowSpan={item.rowSpan}
                                  >
                                    {item.lhb_net_amount ? (item.lhb_net_amount / 10000).toFixed(2) : "-"}
                                  </TableCell>
                                  <TableCell className="text-center" rowSpan={item.rowSpan}>
                                    {item.lhb_trade_amount ? (item.lhb_trade_amount / 10000).toFixed(2) : "-"}
                                  </TableCell>
                                  {/* 上榜原因列每行都显示 */}
                                  <TableCell className="text-sm text-center">{item.reasons || "-"}</TableCell>
                                </>
                              ) : (
                                <>
                                  {/* 上榜原因列每行都显示 */}
                                  <TableCell className="text-sm text-center">{item.reasons || "-"}</TableCell>
                                </>
                              )}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="summary" className="mt-4">
          <div className="p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <p className="text-gray-600 dark:text-gray-400 text-sm">在这里显示汇总数据的表格</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default DragonTiger;
