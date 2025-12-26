/**
 * 页面字段解释配置
 * 根据路由路径和查询参数匹配对应的解释内容
 */

export const pageExplanations = {
  "/dragon-tiger": {
    // 每日龙虎榜 Tab
    daily: {
      title: "每日龙虎榜字段说明",
      fields: [
        {
          name: "股票代码/名称",
          description: "A股市场的股票标识符和名称，用于唯一识别一只股票"
        },
        {
          name: "收盘价",
          description: "当日交易结束时的最后成交价格"
        },
        {
          name: "涨跌幅(%)",
          description: "相对于前一交易日收盘价的价格变动百分比。红色表示上涨，绿色表示下跌"
        },
        {
          name: "换手率(%)",
          description: "当日成交量占流通股本的比例，反映股票的活跃程度。换手率越高，交易越活跃"
        },
        {
          name: "龙虎榜净买额(万)",
          description: "上榜席位的买入金额减去卖出金额。正值表示净买入，负值表示净卖出"
        },
        {
          name: "龙虎榜成交额(万)",
          description: "上榜席位的总成交金额（买入+卖出），反映大资金的参与程度"
        },
        {
          name: "龙虎榜买入额(万)",
          description: "上榜席位的买入总金额，数值越大说明买方力量越强"
        },
        {
          name: "龙虎榜卖出额(万)",
          description: "上榜席位的卖出总金额，数值越大说明卖方力量越强"
        },
        {
          name: "流通市值(亿)",
          description: "股票的流通股本乘以当前股价，反映该股票在市场上的流通规模"
        },
        {
          name: "市场总成交额(万)",
          description: "该股票当日在整个市场的总成交金额，用于计算龙虎榜资金占比"
        },
        {
          name: "净买额占比(%)",
          description: "龙虎榜净买额占市场总成交额的百分比，正值越大说明上榜资金买入意愿越强"
        },
        {
          name: "成交额占比(%)",
          description: "龙虎榜成交额占市场总成交额的百分比，反映上榜资金的活跃程度"
        },
        {
          name: "上榜原因",
          description: "股票登上龙虎榜的触发条件，如'日涨幅偏离值达7%'、'日振幅值达15%'等"
        }
      ]
    },

    // 每日机构榜 Tab
    "daily-brokerage": {
      title: "每日机构榜字段说明",
      fields: [
        {
          name: "营业部代码/名称",
          description: "证券营业部的唯一标识和名称"
        },
        {
          name: "买入个股数",
          description: "该营业部当日买入并上榜的股票数量"
        },
        {
          name: "卖出个股数",
          description: "该营业部当日卖出并上榜的股票数量"
        },
        {
          name: "买入总金额(万)",
          description: "该营业部当日所有买入股票的总金额"
        },
        {
          name: "卖出总金额(万)",
          description: "该营业部当日所有卖出股票的总金额"
        },
        {
          name: "总买卖净额(万)",
          description: "买入总金额减去卖出总金额。正值表示净买入，负值表示净卖出。可用于判断营业部的操作方向"
        },
        {
          name: "买入股票",
          description: "该营业部当日买入的具体股票列表"
        }
      ]
    },

    // 范围龙虎榜 Tab
    "date-range": {
      title: "范围龙虎榜字段说明",
      fields: [
        {
          name: "日期",
          description: "股票上榜的具体日期"
        },
        {
          name: "股票代码/名称",
          description: "A股市场的股票标识符和名称"
        },
        {
          name: "收盘价",
          description: "该日期的收盘价格"
        },
        {
          name: "涨跌幅(%)",
          description: "该日期相对于前一交易日的价格变动百分比"
        },
        {
          name: "换手率(%)",
          description: "该日期的成交量占流通股本的比例"
        },
        {
          name: "龙虎榜净买额(万)",
          description: "该日期上榜席位的净买入金额"
        },
        {
          name: "龙虎榜成交额(万)",
          description: "该日期上榜席位的总成交金额"
        },
        {
          name: "龙虎榜买入额(万)",
          description: "该日期上榜席位的买入总金额，数值越大说明买方力量越强"
        },
        {
          name: "龙虎榜卖出额(万)",
          description: "该日期上榜席位的卖出总金额，数值越大说明卖方力量越强"
        },
        {
          name: "流通市值(亿)",
          description: "该日期股票的流通股本乘以收盘价，反映该股票在市场上的流通规模"
        },
        {
          name: "市场总成交额(万)",
          description: "该股票在该日期的市场总成交金额，用于计算龙虎榜资金占比"
        },
        {
          name: "净买额占比(%)",
          description: "龙虎榜净买额占市场总成交额的百分比，正值越大说明上榜资金买入意愿越强"
        },
        {
          name: "成交额占比(%)",
          description: "龙虎榜成交额占市场总成交额的百分比，反映上榜资金的活跃程度"
        },
        {
          name: "上榜原因",
          description: "该日期的上榜触发条件。同一股票可能在不同日期有多个上榜原因"
        },
      ]
    },

    // 分析与总结 Tab
    summary: {
      title: "分析与总结说明",
      fields: [
        {
          name: "活跃营业部分析",
          description: "展示在选定日期范围内最活跃的营业部，包括其买入卖出行为统计"
        },
        {
          name: "多次上榜股票",
          description: "统计在时间范围内多次登上龙虎榜的股票，反映持续受到资金关注的标的"
        },
        {
          name: "趋势图表",
          description: "通过可视化图表展示资金流向、上榜频次等数据趋势"
        }
      ]
    }
  }
};

/**
 * 根据当前路由获取字段解释内容
 * @param {string} pathname - 路由路径
 * @param {URLSearchParams} searchParams - URL查询参数
 * @returns {object|null} 解释内容对象，如果没有匹配则返回null
 */
export function getExplanationForRoute(pathname, searchParams) {
  const pageConfig = pageExplanations[pathname];
  
  if (!pageConfig) {
    return null;
  }

  // 获取tab参数，默认为第一个tab
  const tab = searchParams.get("tab") || Object.keys(pageConfig)[0];
  
  return pageConfig[tab] || null;
}
