import request from '../lib/request';

/**
 * 龙虎榜相关 API
 */

/**
 * 获取最近N天的龙虎榜数据
 * @param {number} daysBack - 查询最近几天的数据，默认7天
 * @returns {Promise} 返回龙虎榜数据
 */
export const getDailyDragonTiger = (daysBack = 7) => {
  const params = {
    daysBack,
  };

  return request({
    url: '/api/dragon-tiger/daily',
    method: 'GET',
    params,
  });
};

/**
 * 获取指定日期范围的龙虎榜数据
 * @param {string} startDate - 开始日期 (格式: YYYYMMDD)
 * @param {string} endDate - 结束日期 (格式: YYYYMMDD)
 * @returns {Promise} 返回龙虎榜数据
 */
export const getDragonTigerByRange = (startDate, endDate) => {
  const params = {
    startDate,
    endDate,
  };

  return request({
    url: '/api/dragon-tiger/range',
    method: 'GET',
    params,
  });
};
