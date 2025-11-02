import api from './api';

// 股票相关 API
export const stocksAPI = {
  // 添加新股票
  addStock: code => api.post('/stocks/AddStock', { code }),

  // 获取股票列表
  getStocks: params => api.get('/stocks', { params }),

  // 获取股票详情
  getStock: code => api.get(`/stocks/${code}`),

  // 搜索股票
  searchStocks: keyword => api.get('/stocks/search', { params: { keyword } }),

  // 更新股票数据
  updateStocks: (source = 'all') => api.post('/update/stocks', { source }),
};

// 健康检查
export const healthCheck = () => api.get('/health');
