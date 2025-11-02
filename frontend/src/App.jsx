import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Layout from './components/Layout';
import HomePage from './pages/home/HomePage';
import StockListPage from './pages/stocklist/StockListPage';
import StockDetailPage from './pages/stockdetail/StockDetailPage';
import './App.scss';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Layout>
          <Routes>
            <Route path='/' element={<HomePage />} />
            <Route path='/stocks' element={<StockListPage />} />
            {/* <Route path='/stocks/:code' element={<StockDetailPage />} /> */}
          </Routes>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;
