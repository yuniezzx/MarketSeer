import { useState, useEffect } from "react";
import dayjs from "dayjs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DataTableWithToggle } from "@/components/ui/data-table";
import { DataTableColumnToggle } from "@/components/ui/data-table-column-toggle";
import { getDailyDragonTiger, getDragonTigerByRange, getDailyActiveBrokerage } from "@/api/dragonTiger";
import { aggregateReasons, groupDataByDate } from "@/lib/utils";
import { INITIAL_DATE } from "@/lib/constants";
import { dailyColumns, rangeColumns, brokerageColumns } from "./columns";
import DragonTigerAnalysis from "./analysis";

function DragonTiger() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 计算开始日期：前一个星期，但不超过2025/12/01
  const defaultStartDate = dayjs().subtract(7, "days");
  const cutoffDate = dayjs(INITIAL_DATE);
  const startDateValue = defaultStartDate.isBefore(cutoffDate) ? cutoffDate : defaultStartDate;

  // ===== 日期和时间相关状态 =====
  const [startDate, setStartDate] = useState(startDateValue.format("YYYY-MM-DD"));
  const [endDate, setEndDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [daysBack, setDaysBack] = useState(7);

  // 每日模式数据
  const [dragonTigerData, setDragonTigerData] = useState([]);

  // 每日机构数据
  const [brokerageData, setBrokerageData] = useState([]);

  // 日期范围模式数据
  const [rawRangeData, setRawRangeData] = useState([]); // 存储原始数据
  const [rangeData, setRangeData] = useState([]);
  const [filterOptions, setFilterOptions] = useState({
    excludeST: true, // 排除ST股票
    changePercentMin: "", // 涨跌幅最小值
    changePercentMax: "", // 涨跌幅最大值
    turnoverRateMin: "", // 换手率最小值
    turnoverRateMax: "", // 换手率最大值
    closePriceMin: "", // 收盘价最小值
    closePriceMax: "", // 收盘价最大值
  });

  // 页面首次加载时自动获取股票
  useEffect(() => {
    handleDailyQuery();
    handleBrokerageQuery();
    handleRangeQuery();
  }, []);

  // 监听原始数据和过滤选项变化，生成显示数据
  useEffect(() => {
    if (rawRangeData.length > 0) {
      const filteredData = filterStocks(rawRangeData, filterOptions);
      setRangeData(filteredData);
    } else {
      setRangeData([]);
    }
  }, [rawRangeData, filterOptions]);

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

  // 查询每日机构数据
  const handleBrokerageQuery = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDailyActiveBrokerage(daysBack);
      if (response.status === "success") {
        // 将数据按日期分组
        const groupedData = groupDataByDate(response.data);
        setBrokerageData(groupedData);
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
        // 聚合数据：将同一只股票的多个上榜原因合并
        const aggregated = aggregateReasons(response.data);
        setRawRangeData(aggregated);
      } else {
        setError(response.message || "查询失败");
      }
    } catch (err) {
      setError(err.message || "网络请求失败");
    } finally {
      setLoading(false);
    }
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

      // 收盘价区间过滤
      const closePriceMin = options.closePriceMin ? parseFloat(options.closePriceMin) : null;
      const closePriceMax = options.closePriceMax ? parseFloat(options.closePriceMax) : null;

      if (closePriceMin !== null && stock.close_price < closePriceMin) {
        return false;
      }
      if (closePriceMax !== null && stock.close_price > closePriceMax) {
        return false;
      }

      return true;
    });
  };

  return (
    <div className="p-6">
      {/* <dic onClick={() => console.log(brokerageData)}>Click</dic> */}
      <Tabs defaultValue="daily" className="w-full">
        <TabsList className="w-fit grid grid-cols-4">
          <TabsTrigger value="daily" className="text-sm">
            每日龙虎榜
          </TabsTrigger>
          <TabsTrigger value="daily-brokerage" className="text-sm">
            每日机构榜
          </TabsTrigger>
          <TabsTrigger value="date-range" className="text-sm">
            范围龙虎榜
          </TabsTrigger>
          <TabsTrigger value="summary" className="text-sm">
            分析与总结
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
                    const date = dateGroup.date;
                    const records = dateGroup.data;
                    const totalRecords = dragonTigerData.reduce((sum, group) => sum + group.data.length, 0);

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

                        <DataTableWithToggle columns={dailyColumns} data={records} loading={false}>
                          {table => <DataTableColumnToggle table={table} />}
                        </DataTableWithToggle>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="daily-brokerage" className="mt-4">
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
                onClick={handleBrokerageQuery}
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

              {!loading && !error && brokerageData.length === 0 && (
                <p className="text-gray-600 dark:text-gray-400 text-sm">设置天数后点击查询按钮查看最近N天的机构数据</p>
              )}

              {!loading && brokerageData.length > 0 && (
                <div className="space-y-6">
                  {brokerageData.map((dateGroup, groupIndex) => {
                    const date = dateGroup.date;
                    const records = dateGroup.data;
                    const totalRecords = brokerageData.reduce((sum, group) => sum + group.data.length, 0);

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

                        <DataTableWithToggle
                          columns={brokerageColumns}
                          data={records}
                          loading={false}
                          enablePagination={true}
                          pageSize={20}
                        >
                          {table => <DataTableColumnToggle table={table} />}
                        </DataTableWithToggle>
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
                  <label className="text-sm font-medium">收盘价:</label>
                  <Input
                    type="number"
                    placeholder="最小值"
                    value={filterOptions.closePriceMin}
                    onChange={e => setFilterOptions(prev => ({ ...prev, closePriceMin: e.target.value }))}
                    className="w-20"
                    step="0.01"
                    size="sm"
                  />
                  <span className="text-sm text-gray-500">-</span>
                  <Input
                    type="number"
                    placeholder="最大值"
                    value={filterOptions.closePriceMax}
                    onChange={e => setFilterOptions(prev => ({ ...prev, closePriceMax: e.target.value }))}
                    className="w-20"
                    step="0.01"
                    size="sm"
                  />
                </div>
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

                  <DataTableWithToggle columns={rangeColumns} data={rangeData} loading={loading}>
                    {table => <DataTableColumnToggle table={table} />}
                  </DataTableWithToggle>
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="summary" className="mt-4">
          <DragonTigerAnalysis
            dailyData={dragonTigerData}
            brokerageData={brokerageData}
            rangeData={rangeData}
            daysBack={daysBack}
            dateRange={{ startDate, endDate }}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default DragonTiger;
