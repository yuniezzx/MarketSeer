import api from './api';

// 龙虎榜相关 API
export const lhbAPI = {
  // 获取日期内龙虎榜数据
  getLhbByDate: (startDate, endDate) => api.get('/lhb/getLhbByDate', { params: { startDate, endDate } }),
};
