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
    // 鉴权 header 注入（如果有 token）
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 可以在这里添加其他全局请求配置
    return config;
  },
  error => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器（带重试逻辑）
api.interceptors.response.use(
  response => {
    // 统一返回 data 字段
    return response.data;
  },
  async error => {
    // 统一错误处理
    const { response, config } = error;

    // 网络错误
    if (!response) {
      console.error('Network Error:', error.message);
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: '网络连接失败，请检查网络设置',
      });
    }

    // HTTP 状态码错误处理
    const { status, data } = response;

    switch (status) {
      case 401:
        // 未授权，清除 token 并跳转到登录页
        localStorage.removeItem('token');
        console.error('Unauthorized:', data?.message || '请重新登录');
        // window.location.href = '/login'; // 如果需要自动跳转
        return Promise.reject({
          code: 'UNAUTHORIZED',
          message: data?.message || '未授权，请重新登录',
        });

      case 403:
        console.error('Forbidden:', data?.message || '无权限访问');
        return Promise.reject({
          code: 'FORBIDDEN',
          message: data?.message || '无权限访问此资源',
        });

      case 404:
        console.error('Not Found:', data?.message || '资源不存在');
        return Promise.reject({
          code: 'NOT_FOUND',
          message: data?.message || '请求的资源不存在',
        });

      case 500:
      case 502:
      case 503:
        // 服务器错误，尝试重试（最多3次）
        config.__retryCount = config.__retryCount || 0;

        if (config.__retryCount < 3) {
          config.__retryCount += 1;
          console.warn(`Retrying request (${config.__retryCount}/3):`, config.url);

          // 延迟重试（指数退避）
          await new Promise(resolve => setTimeout(resolve, 1000 * config.__retryCount));

          return api.request(config);
        }

        console.error('Server Error:', data?.message || '服务器错误');
        return Promise.reject({
          code: 'SERVER_ERROR',
          message: data?.message || '服务器错误，请稍后重试',
        });

      default:
        console.error('API Error:', error);
        return Promise.reject({
          code: 'UNKNOWN_ERROR',
          message: data?.message || error.message || '未知错误',
        });
    }
  }
);

export default api;
