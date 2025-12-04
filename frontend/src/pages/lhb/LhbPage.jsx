import React, { useState, useEffect, useMemo } from 'react';
import dayjs from 'dayjs';
import { DatePicker, Button, Space, Table, message, InputNumber, Input, Tooltip } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { lhbAPI, stocksAPI } from '../../services';
import { getTurnoverRateClass } from '../../utils/turnoverRateHelper';
import './LhbPage.scss';

const LhbPage = () => {
  const [startDate, setStartDate] = useState(dayjs().subtract(14, 'day') > dayjs('2025-12-01') ? dayjs().subtract(14, 'day') : dayjs('2025-12-01'));
  const [endDate, setEndDate] = useState(dayjs());
  const [loading, setLoading] = useState(false);
  const [lhbData, setLhbData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 100,
    total: 0,
  });

  // Sort states
  const [sortField, setSortField] = useState(null);
  const [sortOrder, setSortOrder] = useState(null);

  // Filter states
  const [filterStockCode, setFilterStockCode] = useState('');
  const [filterStockName, setFilterStockName] = useState('');
  const [filterStartDate, setFilterStartDate] = useState(null);
  const [filterEndDate, setFilterEndDate] = useState(null);
  const [closePriceMin, setClosePriceMin] = useState(null);
  const [closePriceMax, setClosePriceMax] = useState(null);
  const [turnoverRateMin, setTurnoverRateMin] = useState(null);
  const [turnoverRateMax, setTurnoverRateMax] = useState(null);

  // Calculate stock listing count
  const stockCountMap = useMemo(() => {
    const countMap = {};
    lhbData.forEach(item => {
      if (item.code) {
        countMap[item.code] = (countMap[item.code] || 0) + 1;
      }
    });
    return countMap;
  }, [lhbData]);

  const filterLhbItem = item => {
    // Filter by stock code
    if (filterStockCode && item.code) {
      if (!item.code.toLowerCase().includes(filterStockCode.toLowerCase())) return false;
    }

    // Filter by stock name
    if (filterStockName && item.name) {
      if (!item.name.toLowerCase().includes(filterStockName.toLowerCase())) return false;
    }

    // Filter by listing date range
    if (filterStartDate) {
      const itemDate = dayjs(item.listed_date);
      if (itemDate.isBefore(filterStartDate, 'day')) return false;
    }
    if (filterEndDate) {
      const itemDate = dayjs(item.listed_date);
      if (itemDate.isAfter(filterEndDate, 'day')) return false;
    }

    // Filter by close price
    if (closePriceMin !== null && closePriceMin !== undefined) {
      const price = Number(item.close_price);
      if (isNaN(price) || price < closePriceMin) return false;
    }
    if (closePriceMax !== null && closePriceMax !== undefined) {
      const price = Number(item.close_price);
      if (isNaN(price) || price > closePriceMax) return false;
    }

    // Filter by turnover rate
    if (turnoverRateMin !== null && turnoverRateMin !== undefined) {
      const rate = Number(item.turnover_rate);
      if (isNaN(rate) || rate < turnoverRateMin) return false;
    }
    if (turnoverRateMax !== null && turnoverRateMax !== undefined) {
      const rate = Number(item.turnover_rate);
      if (isNaN(rate) || rate > turnoverRateMax) return false;
    }

    return true;
  };

  const filteredData = useMemo(() => {
    const filtered = lhbData.filter(filterLhbItem);

    // Apply sorting
    return filtered.sort((a, b) => {
      // If there's a custom sort field, apply it first
      if (sortField && sortOrder) {
        let compareResult = 0;

        if (sortField === 'listing_count') {
          compareResult = (stockCountMap[a.code] || 0) - (stockCountMap[b.code] || 0);
        } else if (sortField === 'listed_date') {
          compareResult = dayjs(a.listed_date).unix() - dayjs(b.listed_date).unix();
        } else if (['close_price', 'change_percent', 'turnover_rate', 'lhb_buy_amount', 'lhb_sell_amount', 'lhb_net_amount', 'lhb_trade_amount', 'market_total_amount'].includes(sortField)) {
          compareResult = Number(a[sortField] || 0) - Number(b[sortField] || 0);
        }

        if (compareResult !== 0) {
          return sortOrder === 'ascend' ? compareResult : -compareResult;
        }
      }

      // Default sort: by listed_date (desc), then by code (asc) to group same stocks on same date together
      const dateCompare = dayjs(b.listed_date).unix() - dayjs(a.listed_date).unix();
      if (dateCompare !== 0) return dateCompare;
      return (a.code || '').localeCompare(b.code || '');
    });
  }, [lhbData, filterStockCode, filterStockName, filterStartDate, filterEndDate, closePriceMin, closePriceMax, turnoverRateMin, turnoverRateMax, sortField, sortOrder, stockCountMap]);

  // Calculate current page data for rowSpan calculation
  const currentPageData = useMemo(() => {
    const { current, pageSize } = pagination;
    const start = (current - 1) * pageSize;
    const end = start + pageSize;
    return filteredData.slice(start, end);
  }, [filteredData, pagination]);

  // Calculate rowSpan for merged cells
  const rowSpanMap = useMemo(() => {
    const map = new Map();

    currentPageData.forEach((record, index) => {
      const key = `${record.listed_date}-${record.code}`;

      if (!map.has(key)) {
        // Count consecutive rows with same date and code
        let count = 1;
        for (let i = index + 1; i < currentPageData.length; i++) {
          const nextRecord = currentPageData[i];
          if (nextRecord.listed_date === record.listed_date && nextRecord.code === record.code) {
            count++;
          } else {
            break;
          }
        }
        map.set(key, { startIndex: index, count });
      }
    });

    return map;
  }, [currentPageData]);

  // Helper function to get rowSpan for a cell
  const getRowSpan = (record, index) => {
    const key = `${record.listed_date}-${record.code}`;
    const info = rowSpanMap.get(key);

    if (!info) return 1;

    if (index === info.startIndex) {
      return info.count;
    }
    return 0;
  };

  // Helper function to check if cell should have merged background
  const isMergedCell = (record, index) => {
    const key = `${record.listed_date}-${record.code}`;
    const info = rowSpanMap.get(key);
    return info && info.count > 1 && index === info.startIndex;
  };

  const columns = useMemo(
    () => [
      {
        title: '上榜次数',
        dataIndex: 'listing_count',
        key: 'listing_count',
        width: 100,
        align: 'center',
        sorter: (a, b) => (stockCountMap[a.code] || 0) - (stockCountMap[b.code] || 0),
        render: (_, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          return {
            children: stockCountMap[record.code] || 0,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '上榜日期',
        dataIndex: 'listed_date',
        key: 'listed_date',
        width: 110,
        sorter: (a, b) => dayjs(a.listed_date).unix() - dayjs(b.listed_date).unix(),
        render: (text, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          return {
            children: text,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },

      {
        title: '股票代码',
        dataIndex: 'code',
        key: 'code',
        width: 100,
        render: (text, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          return {
            children: text,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '股票名称',
        dataIndex: 'name',
        key: 'name',
        width: 120,
        render: (text, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          return {
            children: (
              <Tooltip title={`将 ${text} (${record.code}) 添加到股票列表`}>
                <Button size='small' type='link' color='primary' variant='text' onClick={() => handleAddStock(record.code)}>
                  {text}
                </Button>
              </Tooltip>
            ),
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '收盘价',
        dataIndex: 'close_price',
        key: 'close_price',
        width: 100,
        align: 'center',
        sorter: (a, b) => Number(a.close_price || 0) - Number(b.close_price || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          const displayValue = val ? `¥${Number(val).toFixed(2)}` : '-';
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '涨跌幅(%)',
        dataIndex: 'change_percent',
        key: 'change_percent',
        width: 110,
        align: 'center',
        sorter: (a, b) => Number(a.change_percent || 0) - Number(b.change_percent || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          let displayValue = '-';
          if (val) {
            const num = Number(val);
            const color = num > 0 ? 'red' : num < 0 ? 'green' : 'inherit';
            displayValue = (
              <span style={{ color }}>
                {num > 0 ? '+' : ''}
                {num.toFixed(2)}%
              </span>
            );
          }
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '换手率(%)',
        dataIndex: 'turnover_rate',
        key: 'turnover_rate',
        width: 110,
        align: 'center',
        sorter: (a, b) => Number(a.turnover_rate || 0) - Number(b.turnover_rate || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          let displayValue = '-';
          if (val) {
            const rate = Number(val);
            const className = getTurnoverRateClass(rate);
            displayValue = <span className={className}>{rate.toFixed(2)}%</span>;
          }
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '龙虎榜买入额',
        dataIndex: 'lhb_buy_amount',
        key: 'lhb_buy_amount',
        width: 140,
        align: 'center',
        sorter: (a, b) => Number(a.lhb_buy_amount || 0) - Number(b.lhb_buy_amount || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          let displayValue = '-';
          if (val) {
            const amount = Number(val);
            if (amount >= 100000000) {
              displayValue = `¥${(amount / 100000000).toFixed(2)}亿`;
            } else if (amount >= 10000) {
              displayValue = `¥${(amount / 10000).toFixed(2)}万`;
            } else {
              displayValue = `¥${amount.toFixed(2)}`;
            }
          }
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '龙虎榜卖出额',
        dataIndex: 'lhb_sell_amount',
        key: 'lhb_sell_amount',
        width: 140,
        align: 'center',
        sorter: (a, b) => Number(a.lhb_sell_amount || 0) - Number(b.lhb_sell_amount || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          let displayValue = '-';
          if (val) {
            const amount = Number(val);
            if (amount >= 100000000) {
              displayValue = `¥${(amount / 100000000).toFixed(2)}亿`;
            } else if (amount >= 10000) {
              displayValue = `¥${(amount / 10000).toFixed(2)}万`;
            } else {
              displayValue = `¥${amount.toFixed(2)}`;
            }
          }
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '龙虎榜净买额',
        dataIndex: 'lhb_net_amount',
        key: 'lhb_net_amount',
        width: 140,
        align: 'center',
        sorter: (a, b) => Number(a.lhb_net_amount || 0) - Number(b.lhb_net_amount || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          let displayValue = '-';
          if (val || val === 0) {
            const amount = Number(val);
            const color = amount > 0 ? 'red' : amount < 0 ? 'green' : 'inherit';
            const absAmount = Math.abs(amount);
            let amountStr;
            if (absAmount >= 100000000) {
              amountStr = `${(absAmount / 100000000).toFixed(2)}亿`;
            } else if (absAmount >= 10000) {
              amountStr = `${(absAmount / 10000).toFixed(2)}万`;
            } else {
              amountStr = absAmount.toFixed(2);
            }
            displayValue = (
              <span style={{ color }}>
                {amount > 0 ? '+' : amount < 0 ? '-' : ''}¥{amountStr}
              </span>
            );
          }
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '龙虎榜成交额',
        dataIndex: 'lhb_trade_amount',
        key: 'lhb_trade_amount',
        width: 140,
        align: 'center',
        sorter: (a, b) => Number(a.lhb_trade_amount || 0) - Number(b.lhb_trade_amount || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          let displayValue = '-';
          if (val) {
            const amount = Number(val);
            if (amount >= 100000000) {
              displayValue = `¥${(amount / 100000000).toFixed(2)}亿`;
            } else if (amount >= 10000) {
              displayValue = `¥${(amount / 10000).toFixed(2)}万`;
            } else {
              displayValue = `¥${amount.toFixed(2)}`;
            }
          }
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '市场总成交额',
        dataIndex: 'market_total_amount',
        key: 'market_total_amount',
        width: 140,
        align: 'center',
        sorter: (a, b) => Number(a.market_total_amount || 0) - Number(b.market_total_amount || 0),
        render: (val, record, index) => {
          const rowSpan = getRowSpan(record, index);
          const isMerged = isMergedCell(record, index);
          let displayValue = '-';
          if (val) {
            const amount = Number(val);
            if (amount >= 100000000) {
              displayValue = `¥${(amount / 100000000).toFixed(2)}亿`;
            } else if (amount >= 10000) {
              displayValue = `¥${(amount / 10000).toFixed(2)}万`;
            } else {
              displayValue = `¥${amount.toFixed(2)}`;
            }
          }
          return {
            children: displayValue,
            props: {
              rowSpan,
              style: isMerged ? { backgroundColor: '#f0f5ff' } : {},
            },
          };
        },
      },
      {
        title: '上榜原因',
        dataIndex: 'reasons',
        key: 'reasons',
        width: 200,
      },
      {
        title: '解读',
        dataIndex: 'analysis',
        key: 'analysis',
        width: 250,
      },
    ],
    [stockCountMap, getRowSpan, isMergedCell]
  );

  const fetchLhbData = async () => {
    setLoading(true);
    try {
      const response = await lhbAPI.getLhbByDate(startDate.format('YYYY-MM-DD'), endDate.format('YYYY-MM-DD'));

      if (response.status === 'success') {
        setLhbData(response.data);
        setPagination(prev => ({
          ...prev,
          total: response.data.length,
        }));
      }
    } catch (error) {
      message.error('获取龙虎榜数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = () => {
    if (startDate.isAfter(endDate)) {
      message.warning('开始日期不能晚于结束日期');
      return;
    }
    fetchLhbData();
  };

  const handleTableChange = (newPagination, filters, sorter) => {
    setPagination(newPagination);

    // Handle sorting
    if (sorter && sorter.field) {
      setSortField(sorter.field);
      setSortOrder(sorter.order);
    } else {
      setSortField(null);
      setSortOrder(null);
    }
  };

  const handleResetFilters = () => {
    setFilterStockCode('');
    setFilterStockName('');
    setFilterStartDate(null);
    setFilterEndDate(null);
    setClosePriceMin(null);
    setClosePriceMax(null);
    setTurnoverRateMin(null);
    setTurnoverRateMax(null);
  };

  const handleAddStock = async code => {
    try {
      const response = await stocksAPI.addStock(code);
      if (response.status === 'success') {
        message.success(`股票 ${code} 添加成功`);
      }
    } catch (error) {
      message.error(`添加股票失败: ${error.message || '未知错误'}`);
      console.error(error);
    }
  };

  useEffect(() => {
    fetchLhbData();
  }, []);

  return (
    <div className='lhb-page'>
      <div className='page-header'>
        <h2>龙虎榜</h2>
        <Space>
          <DatePicker placeholder='开始日期' value={startDate} minDate={dayjs('2025-12-01')} maxDate={endDate} onChange={setStartDate} style={{ width: 200 }} />
          <DatePicker placeholder='结束日期' value={endDate} maxDate={dayjs().subtract(1, 'day')} onChange={setEndDate} style={{ width: 200 }} />
          <Button type='primary' onClick={handleUpdate}>
            更新
          </Button>
        </Space>
      </div>

      <div className='filter-section'>
        <Space direction='vertical' size='middle' style={{ width: '100%' }}>
          <Space size='large' wrap>
            <Space>
              <span>股票代码:</span>
              <Input size='small' placeholder='输入代码' value={filterStockCode} onChange={e => setFilterStockCode(e.target.value)} style={{ width: 120 }} allowClear />
            </Space>

            <Space>
              <span>股票名称:</span>
              <Input size='small' placeholder='输入名称' value={filterStockName} onChange={e => setFilterStockName(e.target.value)} style={{ width: 120 }} allowClear />
            </Space>
          </Space>

          <Space size='large' wrap>
            <Space>
              <span>上榜日期:</span>
              <DatePicker size='small' placeholder='开始日期' value={filterStartDate} minDate={startDate} maxDate={endDate} onChange={setFilterStartDate} style={{ width: 120 }} />
              <span>-</span>
              <DatePicker size='small' placeholder='结束日期' value={filterEndDate} minDate={startDate} maxDate={endDate} onChange={setFilterEndDate} style={{ width: 120 }} />
            </Space>

            <Space>
              <span>收盘价:</span>
              <InputNumber size='small' placeholder='最小值' value={closePriceMin} onChange={setClosePriceMin} min={0} precision={2} style={{ width: 120 }} />
              <span>-</span>
              <InputNumber size='small' placeholder='最大值' value={closePriceMax} onChange={setClosePriceMax} min={0} precision={2} style={{ width: 120 }} />
            </Space>

            <Space>
              <span>换手率(%):</span>
              <InputNumber size='small' placeholder='最小值' value={turnoverRateMin} onChange={setTurnoverRateMin} min={0} precision={2} style={{ width: 120 }} />
              <span>-</span>
              <InputNumber size='small' placeholder='最大值' value={turnoverRateMax} onChange={setTurnoverRateMax} min={0} precision={2} style={{ width: 120 }} />
            </Space>

            <Button onClick={handleResetFilters}>重置筛选</Button>

            <span style={{ color: '#666' }}>
              显示: {filteredData.length} / {lhbData.length} 条数据
            </span>
          </Space>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={currentPageData}
        rowKey={record => `${record.id}`}
        loading={loading}
        pagination={{
          ...pagination,
          total: filteredData.length,
        }}
        onChange={handleTableChange}
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
};

export default LhbPage;
