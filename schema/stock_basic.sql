-- schema/stock_basic.sql
-- Full DDL for stock_basic (copied from pipeline/init.py). Idempotent.
CREATE TABLE IF NOT EXISTS stock_basic (
  symbol TEXT NOT NULL, -- 股票代码
  name TEXT, -- 股票名称
  short_name TEXT, -- 股票简称
  full_name TEXT, -- 公司全称
  exchange TEXT, -- 交易所
  industry TEXT, -- 行业
  industry_code TEXT, -- 行业编码
  list_date TEXT, -- 上市日期（字符串）
  listed_date INTEGER, -- 上市时间（时间戳）
  website TEXT, -- 公司网站
  total_shares REAL, -- 总股本
  float_shares REAL, -- 流通股
  total_market_cap REAL, -- 总市值
  float_market_cap REAL, -- 流通市值
  net_profit REAL, -- 净利润
  pe REAL, -- 市盈率
  pb REAL, -- 市净率
  roe REAL, -- ROE
  gross_margin REAL, -- 毛利率
  net_margin REAL, -- 净利率
  org_id TEXT, -- 机构ID
  org_name_cn TEXT, -- 公司中文全称
  org_short_name_cn TEXT, -- 公司中文简称
  org_name_en TEXT, -- 公司英文全称
  main_operation_business TEXT, -- 主营业务
  operating_scope TEXT, -- 经营范围
  district_encode TEXT, -- 地区编码
  org_cn_introduction TEXT, -- 公司中文简介
  legal_representative TEXT, -- 法定代表人
  general_manager TEXT, -- 总经理
  secretary TEXT, -- 董秘
  established_date INTEGER, -- 成立日期（时间戳）
  reg_asset REAL, -- 注册资本
  staff_num INTEGER, -- 员工人数
  telephone TEXT, -- 电话
  postcode TEXT, -- 邮编
  fax TEXT, -- 传真
  email TEXT, -- 邮箱
  reg_address_cn TEXT, -- 注册地址（中文）
  office_address_cn TEXT, -- 办公地址（中文）
  currency TEXT, -- 币种
  provincial_name TEXT, -- 省份
  actual_controller TEXT, -- 实际控制人
  classi_name TEXT, -- 企业类型
  pre_name_cn TEXT, -- 曾用名（中文）
  chairman TEXT, -- 董事长
  executives_nums INTEGER, -- 高管人数
  actual_issue_vol REAL, -- 实际发行量
  issue_price REAL, -- 发行价
  actual_rc_net_amt REAL, -- 实际募集净额
  pe_after_issuing REAL, -- 发行后市盈率
  online_success_rate_of_issue REAL, -- 网上发行成功率
  updated_at TEXT, -- 更新时间
  PRIMARY KEY(symbol)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stock_symbol ON stock_basic(symbol);
