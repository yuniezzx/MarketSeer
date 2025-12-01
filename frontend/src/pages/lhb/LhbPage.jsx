import React, { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import { DatePicker, Button, Space, Table, message } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { lhbAPI } from '../../services';
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

  const columns = [
    {
      title: '上榜日期',
      dataIndex: 'listed_date',
      key: 'listed_date',
    },
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '收盘价',
      dataIndex: 'close_price',
      key: 'close_price',
      render: val => (val ? `¥${Number(val).toFixed(2)}` : '-'),
    },
    {
      title: '涨跌幅(%)',
      dataIndex: 'change_percent',
      key: 'change_percent',
      render: val => {
        if (!val) return '-';
        const num = Number(val);
        const color = num > 0 ? 'red' : num < 0 ? 'green' : 'inherit';
        return (
          <span style={{ color }}>
            {num > 0 ? '+' : ''}
            {num.toFixed(2)}%
          </span>
        );
      },
    },
    {
      title: '换手率(%)',
      dataIndex: 'turnover_rate',
      key: 'turnover_rate',
      render: val => {
        if (!val) return '-';
        const rate = Number(val);
        const className = getTurnoverRateClass(rate);
        return <span className={className}>{rate.toFixed(2)}%</span>;
      },
    },
    {
      title: '上榜原因',
      dataIndex: 'reasons',
      key: 'reasons',
    },
    {
      title: '解读',
      dataIndex: 'analysis',
      key: 'analysis',
    },
  ];

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
        message.success('数据加载成功');
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

  const handleTableChange = newPagination => {
    setPagination(newPagination);
  };

  useEffect(() => {
    fetchLhbData();
  }, []);

  return (
    <div className='lhb-page'>
      <div className='page-header'>
        <h2>龙虎榜页面</h2>
        <Space>
          <DatePicker placeholder='开始日期' value={startDate} minDate={dayjs('2025-12-01')} maxDate={endDate} onChange={setStartDate} style={{ width: 200 }} />
          <DatePicker placeholder='结束日期' value={endDate} maxDate={dayjs().subtract(1, 'day')} onChange={setEndDate} style={{ width: 200 }} />
          <Button type='primary' onClick={handleUpdate}>
            更新
          </Button>
        </Space>
      </div>

      <Table columns={columns} dataSource={lhbData} rowKey={record => `${record.code}-${record.listed_date}`} loading={loading} pagination={pagination} onChange={handleTableChange} />
    </div>
  );
};

export default LhbPage;
