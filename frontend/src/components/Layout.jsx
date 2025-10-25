import React from 'react';
import { Layout as AntLayout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import { HomeOutlined, StockOutlined } from '@ant-design/icons';
import './Layout.css';

const { Header, Content, Footer } = AntLayout;

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/stocks',
      icon: <StockOutlined />,
      label: '股票列表',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <AntLayout className='layout'>
      <Header className='header'>
        <div className='logo'>MarketSeer</div>
        <Menu
          theme='dark'
          mode='horizontal'
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content className='content'>
        <div className='content-wrapper'>{children}</div>
      </Content>
      <Footer className='footer'>MarketSeer ©2024 - 金融数据采集与分析系统</Footer>
    </AntLayout>
  );
}

export default Layout;
