import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function getTurnoverRateColor(rate) {
  if (rate < 1) return 'text-neutral-stock';
  if (rate < 3) return 'text-primary dark:text-primary';
  if (rate < 7) return 'text-bull';
  if (rate < 15) return 'text-orange-500 dark:text-orange-400';
  if (rate < 30) return 'text-red-600 dark:text-red-400';
  if (rate < 50) return 'text-red-700 dark:text-red-300';
  return 'text-pink-600 dark:text-pink-400';
}

/**
 * 聚合同一天同一只股票的多个上榜原因，或保持营业部数据的唯一性
 * @param {Array} data - 原始数据数组
 * @returns {Array} - 聚合后的数据数组
 */
export function aggregateReasons(data) {
  if (!data || data.length === 0) return [];

  const map = new Map();

  data.forEach(item => {
    // 支持股票数据（code）和营业部数据（brokerage_code）
    const identifier = item.code || item.brokerage_code;
    const key = `${item.listed_date}_${identifier}`;
    if (map.has(key)) {
      // 已存在该股票/营业部，添加原因到数组
      const existing = map.get(key);
      if (item.reasons) {
        existing.reasons.push(item.reasons);
      }
    } else {
      // 新股票/营业部，初始化 reasons 为数组
      map.set(key, {
        ...item,
        reasons: item.reasons ? [item.reasons] : [],
      });
    }
  });

  return Array.from(map.values());
}

/**
 * 将数据按日期分组的函数
 * @param {Array} data - 数据数组
 * @returns {Array} - 分组后的数据数组 [{date: string, data: Array}]
 */
export function groupDataByDate(data) {
  if (!data || data.length === 0) return [];

  const grouped = {};

  data.forEach(item => {
    const date = item.listed_date;
    if (!grouped[date]) {
      grouped[date] = [];
    }
    grouped[date].push(item);
  });

  // 转换为数组格式，按日期降序排列
  return Object.keys(grouped)
    .sort((a, b) => b.localeCompare(a))
    .map(date => ({
      date,
      data: aggregateReasons(grouped[date]),
    }));
}
