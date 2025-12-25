import axios from 'axios';
import { API_BASE_URL, REQUEST_TIMEOUT } from './constants';

// 创建 axios 实例
const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
  },
});

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    // 例如：添加 token
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    console.log('Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  error => {
    // 请求错误时做些什么
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    console.log('Response:', response.status, response.config.url);

    // 直接返回 response.data，简化使用
    return response.data;
  },
  error => {
    // 对响应错误做点什么
    console.error('Response Error:', error);

    // 统一处理错误
    if (error.response) {
      // 请求已发出，但服务器响应的状态码不在 2xx 范围内
      const { status, data } = error.response;

      switch (status) {
        case 400:
          console.error('请求错误(400):', data.message || data.error);
          break;
        case 401:
          console.error('未授权(401)，请重新登录');
          // 可以在这里处理登出逻辑
          break;
        case 404:
          console.error('请求的资源不存在(404)');
          break;
        case 500:
          console.error('服务器错误(500):', data.message || data.error);
          break;
        default:
          console.error(`连接错误(${status})!`);
      }

      return Promise.reject(error.response.data);
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      console.error('网络错误，请检查网络连接');
      return Promise.reject({ message: '网络错误，请检查网络连接' });
    } else {
      // 在设置请求时触发了错误
      console.error('请求配置错误:', error.message);
      return Promise.reject({ message: error.message });
    }
  }
);

export default request;
