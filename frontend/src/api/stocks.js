import request from '../lib/request';

/**
 * 股票相关 API
 */

/**
 * 获取所有股票列表
 * @returns {Promise} 返回股票列表数据
 */
export const getStocks = () => {
  return request({
    url: '/api/stocks',
    method: 'GET',
  });
};

/**
 * 添加新股票
 * @param {string} symbol - 股票代码，例如 "AAPL"
 * @returns {Promise} 返回添加结果
 */
export const addStock = symbol => {
  return request({
    url: '/api/stocks',
    method: 'POST',
    data: {
      symbol,
    },
  });
};
