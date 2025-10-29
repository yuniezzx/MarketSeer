import React from 'react';
import { Card, Row, Col, Typography, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { StockOutlined, LineChartOutlined, DatabaseOutlined } from '@ant-design/icons';
import AddStock from '../../components/AddStock';
import './HomePage.scss';

const { Title, Paragraph } = Typography;

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className='home-page'>
      <div className='hero-section'>
        <Title level={1}>MarketSeer</Title>
        <Paragraph className='subtitle'>金融数据采集、整合与分析系统</Paragraph>
        <Button type='primary' size='small' onClick={() => navigate('/stocks')}>
          开始使用
        </Button>
        <div className='add-stock-btn'>
          <AddStock />
        </div>
      </div>

      <Row gutter={[24, 24]} className='features-section'>
        <Col xs={24} md={8}>
          <Card hoverable className='feature-card'>
            <DatabaseOutlined className='feature-icon' />
            <Title level={3}>多数据源整合</Title>
            <Paragraph>整合 AkShare、eFinance、yFinance 等多个数据源，提供全面的股票市场数据</Paragraph>
          </Card>
        </Col>

        <Col xs={24} md={8}>
          <Card hoverable className='feature-card'>
            <StockOutlined className='feature-icon' />
            <Title level={3}>实时数据更新</Title>
            <Paragraph>支持定时自动更新股票数据，确保数据的时效性和准确性</Paragraph>
          </Card>
        </Col>

        <Col xs={24} md={8}>
          <Card hoverable className='feature-card'>
            <LineChartOutlined className='feature-icon' />
            <Title level={3}>数据可视化</Title>
            <Paragraph>提供直观的图表和统计分析，帮助您更好地理解市场趋势</Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default HomePage;
