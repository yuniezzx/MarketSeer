/**
 * 换手率辅助工具函数
 */

/**
 * 根据换手率获取对应的 CSS 类名
 *
 * 分级规则：
 * - < 20%: 无特殊样式
 * - 20-30%: turnover-20 (橙色)
 * - 30-40%: turnover-30 (深橙色)
 * - 40-50%: turnover-40 (红色)
 * - >= 50%: turnover-50 (深红色，带背景高亮)
 *
 * @param {number} rate - 换手率数值
 * @returns {string} CSS 类名
 */
export const getTurnoverRateClass = rate => {
  if (rate < 20) return '';
  if (rate < 30) return 'turnover-20';
  if (rate < 40) return 'turnover-30';
  if (rate < 50) return 'turnover-40';
  return 'turnover-50';
};

/**
 * 根据换手率获取对应的颜色值
 *
 * @param {number} rate - 换手率数值
 * @returns {string} 颜色值
 */
export const getTurnoverRateColor = rate => {
  if (rate < 20) return '#595959';
  if (rate < 30) return '#faad14';
  if (rate < 40) return '#fa8c16';
  if (rate < 50) return '#f5222d';
  return '#cf1322';
};

/**
 * 格式化换手率显示
 *
 * @param {number} rate - 换手率数值
 * @param {number} decimals - 小数位数，默认 2
 * @returns {string} 格式化后的字符串
 */
export const formatTurnoverRate = (rate, decimals = 2) => {
  if (rate === null || rate === undefined) return '-';
  return `${Number(rate).toFixed(decimals)}%`;
};
