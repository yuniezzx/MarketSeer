import React, { useState, useEffect } from 'react';
import { Table, Input, Button, message, Space, Tag } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { stocksAPI } from '../../services';
import './StockListPage.scss';

function StockListPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [stocks, setStocks] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 50,
    total: 0,
  });
  const [searchKeyword, setSearchKeyword] = useState('');

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code',
      width: 120,
      render: (text, record) => <a onClick={() => navigate(`/stocks/${record.code}`)}>{text}</a>,
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market',
      width: 100,
      render: market => <Tag color='blue'>{market}</Tag>,
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 150,
    },
    {
      title: '上市日期',
      dataIndex: 'list_date',
      key: 'list_date',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: status => <Tag color={status === '上市' ? 'green' : 'red'}>{status}</Tag>,
    },
    {
      title: '数据来源',
      dataIndex: 'source',
      key: 'source',
      width: 120,
    },
  ];

  const fetchStocks = async (page = 1, pageSize = 50) => {
    setLoading(true);
    try {
      const response = await stocksAPI.getStocks({
        page,
        per_page: pageSize,
      });

      if (response.status === 'success') {
        setStocks(response.data);
        setPagination({
          current: page,
          pageSize: pageSize,
          total: response.pagination?.total || 0,
        });
      }
    } catch (error) {
      message.error('获取股票列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchKeyword.trim()) {
      message.warning('请输入搜索关键词');
      return;
    }

    setLoading(true);
    try {
      const response = await stocksAPI.searchStocks(searchKeyword);
      if (response.status === 'success') {
        setStocks(response.data);
        setPagination(prev => ({ ...prev, total: response.data.length }));
      }
    } catch (error) {
      message.error('搜索失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = pagination => {
    fetchStocks(pagination.current, pagination.pageSize);
  };

  const handleRefresh = () => {
    setSearchKeyword('');
    fetchStocks(1, 50);
  };

  useEffect(() => {
    fetchStocks();
  }, []);

  return (
    <div className='stock-list-page'>
      <div className='page-header'>
        <h2>股票列表</h2>
        <Space>
          <Input
            placeholder='搜索股票代码或名称'
            value={searchKeyword}
            onChange={e => setSearchKeyword(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 250 }}
            prefix={<SearchOutlined />}
          />
          <Button type='primary' onClick={handleSearch} icon={<SearchOutlined />}>
            搜索
          </Button>
          <Button onClick={handleRefresh} icon={<ReloadOutlined />}>
            刷新
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={stocks}
        rowKey='id'
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
        scroll={{ x: 1000 }}
      />
    </div>
  );
}

export default StockListPage;
