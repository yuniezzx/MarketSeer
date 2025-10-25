import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// 股票相关 API
export const stockAPI = {
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

export default api;
