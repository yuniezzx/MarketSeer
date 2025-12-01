// 统一导出所有 API 服务
export { stocksAPI, healthCheck } from './stocks';
export { lhbAPI } from './lhb';

// 可以在这里添加其他资源的 API
// export { authAPI } from './auth';
// export { userAPI } from './user';

// 如果需要直接导出 axios 实例
export { default as api } from './api';
