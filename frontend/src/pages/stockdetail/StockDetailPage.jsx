import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Button, message, Spin, Tag } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { stockAPI } from '../../services/api';
import './StockDetailPage.scss';

function StockDetailPage() {
  const { code } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stock, setStock] = useState(null);

  const fetchStockDetail = async () => {
    setLoading(true);
    try {
      const response = await stockAPI.getStock(code);
      if (response.status === 'success') {
        setStock(response.data);
      }
    } catch (error) {
      message.error('获取股票详情失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStockDetail();
  }, [code]);

  if (loading) {
    return (
      <div className='loading-container'>
        <Spin size='large' />
      </div>
    );
  }

  if (!stock) {
    return (
      <div className='error-container'>
        <p>股票信息不存在</p>
        <Button onClick={() => navigate('/stocks')}>返回列表</Button>
      </div>
    );
  }

  return (
    <div className='stock-detail-page'>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/stocks')} style={{ marginBottom: 24 }}>
        返回列表
      </Button>

      <Card title={`${stock.name} (${stock.code})`} className='detail-card'>
        <Descriptions bordered column={2}>
          <Descriptions.Item label='股票代码'>{stock.code}</Descriptions.Item>
          <Descriptions.Item label='股票名称'>{stock.name}</Descriptions.Item>
          <Descriptions.Item label='市场'>
            <Tag color='blue'>{stock.market}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label='行业'>{stock.industry || '-'}</Descriptions.Item>
          <Descriptions.Item label='上市日期'>{stock.list_date || '-'}</Descriptions.Item>
          <Descriptions.Item label='状态'>
            <Tag color={stock.status === '上市' ? 'green' : 'red'}>{stock.status}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label='数据来源'>{stock.source || '-'}</Descriptions.Item>
          <Descriptions.Item label='更新时间'>{stock.update_time || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title='股票分析' className='analysis-card' style={{ marginTop: 24 }}>
        <p style={{ color: '#999' }}>更多分析功能即将推出...</p>
      </Card>
    </div>
  );
}

export default StockDetailPage;
