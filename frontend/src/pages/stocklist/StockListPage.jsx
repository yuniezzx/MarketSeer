import React, { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import { Table, Input, Button, message, Space, Tag, Tooltip } from 'antd';
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
    pageSize: 100,
    total: 0,
  });
  const [searchKeyword, setSearchKeyword] = useState('');

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code',
      render: (text, record) => <a onClick={() => navigate(`/stocks/${record.code}`)}>{text}</a>,
    },
    {
      title: '股票简称',
      dataIndex: 'name',
      key: 'name',
      minWidth: 90,
    },
    {
      title: '股票全称',
      dataIndex: 'full_name',
      key: 'full_name',
      minWidth: 120,
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market',
      render: market => <Tag color='blue'>{market}</Tag>,
    },
    {
      title: '行业代码',
      dataIndex: 'industry_code',
      key: 'industry_code',
      minWidth: 90,
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      minWidth: 120,
    },
    {
      title: '主营业务',
      dataIndex: 'main_operation_business',
      key: 'main_operation_business',
      render: text => (text ? text.trimStart() : '-'),
    },
    {
      title: '经营范围',
      dataIndex: 'operating_scope',
      key: 'operating_scope',
      render: text => {
        const v = text ? text.trimStart() : '-';
        if (v === '-') return '-';
        return (
          <Tooltip title={v} rootClassName='operating-scope-tooltip'>
            <div className='cell-ellipsis'>{v}</div>
          </Tooltip>
        );
      },
    },
    {
      title: '成立日期',
      dataIndex: 'establish_date',
      key: 'establish_date',
      minWidth: 120,
      render: ts => (ts ? dayjs(Number(ts)).format('YYYY-MM-DD') : '-'),
    },
    {
      title: '上市日期',
      dataIndex: 'list_date',
      key: 'list_date',
      minWidth: 120,
      render: ts => (ts ? dayjs(Number(ts)).format('YYYY-MM-DD') : '-'),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: status => <Tag color={status === '上市' ? 'green' : 'red'}>{status}</Tag>,
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
        expandable={{
          expandedRowRender: record => (
            <div className='expanded-row-content'>
              <div className='expanded-section'>
                <strong>主营业务：</strong>
                <p>{record.main_operation_business || '-'}</p>
              </div>
              <div className='expanded-section'>
                <strong>经营范围：</strong>
                <p>{record.operating_scope || '-'}</p>
              </div>
            </div>
          ),
          rowExpandable: record => record.operating_scope || record.main_operation_business,
        }}
        // scroll={{ x: 'max-content' }}
      />
    </div>
  );
}

export default StockListPage;
