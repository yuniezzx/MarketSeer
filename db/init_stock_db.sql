-- 1) 创建数据库
CREATE DATABASE IF NOT EXISTS stock_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE stock_db;

-- 2) 交易所表：统一交易所与地区、时区、货币等
CREATE TABLE IF NOT EXISTS exchange (
  exchange_id     INT PRIMARY KEY AUTO_INCREMENT,
  code            VARCHAR(16) NOT NULL,     -- 例如: SSE, SZSE, HKEX, NASDAQ, NYSE
  mic             VARCHAR(16) NULL,         -- ISO 10383 (如 XSHG, XSHE, XHKG, XNAS, XNYS)
  name            VARCHAR(128) NOT NULL,    -- 上交所、深交所、香港联交所等
  country         VARCHAR(64)  NOT NULL,    -- CN, HK, US...
  timezone        VARCHAR(64)  NOT NULL,    -- Asia/Shanghai, America/New_York ...
  currency        VARCHAR(16)  NOT NULL,    -- CNY, HKD, USD ...
  UNIQUE KEY uq_exchange_code (code),
  UNIQUE KEY uq_exchange_mic (mic)
) ENGINE=InnoDB;

-- 3) 股票主体表：核心唯一标识 + 标准化证券信息
CREATE TABLE IF NOT EXISTS stock (
  stock_id        BIGINT PRIMARY KEY AUTO_INCREMENT,
  exchange_id     INT NOT NULL,
  stock_code      VARCHAR(32) NOT NULL,      -- 本地代码，如 600000, AAPL
  ticker          VARCHAR(64),               -- 标准 ticker
  isin            VARCHAR(32),               -- 国际证券识别码
  short_name      VARCHAR(128) NOT NULL,     -- 简称：腾讯控股
  full_name       VARCHAR(256),              -- 全称：恒宝股份有限公司
  sector          VARCHAR(128),              -- 板块分类，如 科技
  industry        VARCHAR(128),              -- 行业，如 通信设备
  list_date       DATE,                      -- 上市日期
  delist_date     DATE,                      -- 退市日期（可空）
  status          ENUM('active','halted','delisted') NOT NULL DEFAULT 'active',
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_stock_exchange FOREIGN KEY (exchange_id) REFERENCES exchange(exchange_id),
  UNIQUE KEY uq_stock_exchange_code (exchange_id, stock_code),
  UNIQUE KEY uq_stock_ticker_exchange (exchange_id, ticker),
  UNIQUE KEY uq_stock_isin (isin)
) ENGINE=InnoDB;

-- 4) 股票详情表：补充股票主体的企业级信息（公司背景、管理层、注册地址、联系方式等）
CREATE TABLE IF NOT EXISTS stock_details (
  stock_id                 BIGINT NOT NULL,
  org_id                   VARCHAR(32),
  org_name_cn              VARCHAR(256),
  org_short_name_cn        VARCHAR(128),
  org_name_en              VARCHAR(256),
  org_short_name_en        VARCHAR(128),
  pre_name_cn              VARCHAR(256),

  actual_controller        VARCHAR(128),
  legal_representative     VARCHAR(128),
  chairman                 VARCHAR(128),
  general_manager          VARCHAR(128),
  secretary                VARCHAR(128),
  executives_nums          INT,

  classi_name              VARCHAR(64),
  established_date         DATE,
  reg_asset                DECIMAL(20,2),
  staff_num                INT,

  office_address_cn        VARCHAR(256),
  office_address_en        VARCHAR(256),
  reg_address_cn           VARCHAR(256),
  reg_address_en           VARCHAR(256),
  postcode                 VARCHAR(16),
  telephone                VARCHAR(64),
  fax                      VARCHAR(64),
  email                    VARCHAR(128),
  org_website              VARCHAR(128),

  main_operation_business  TEXT,
  operating_scope          TEXT,
  org_cn_introduction      TEXT,

  affiliate_industry_code  VARCHAR(32),
  affiliate_industry_name  VARCHAR(128),

  created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (stock_id),
  CONSTRAINT fk_stock_details FOREIGN KEY (stock_id) REFERENCES stock(stock_id)
) ENGINE=InnoDB;

-- 5) 股票市场信息表：用于记录每只股票的市值、估值、股本结构、最新价格等动态市场数据
-- 适合每日或定期更新，用于估值分析、行情展示、财务指标对比等应用场景
CREATE TABLE IF NOT EXISTS stock_market_info (
  stock_id                 BIGINT NOT NULL,
  stock_code               VARCHAR(16) NOT NULL,
  stock_name               VARCHAR(128),
  latest_price             DECIMAL(10,2),
  total_market_cap         DECIMAL(20,2),
  circulating_market_cap   DECIMAL(20,2),
  total_shares             DECIMAL(20,2),
  circulating_shares       DECIMAL(20,2),
  pe_ratio                 DECIMAL(10,4),
  pb_ratio                 DECIMAL(10,4),
  eps                      DECIMAL(10,4),         -- 每股收益
  navps                    DECIMAL(10,4),         -- 每股净资产
  total_assets             DECIMAL(20,2),         -- 总资产
  industry_name            VARCHAR(128),
  industry_code            VARCHAR(16),
  listed_date              DATE,
  updated_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (stock_id),
  CONSTRAINT fk_market_stock FOREIGN KEY (stock_id) REFERENCES stock(stock_id)
) ENGINE=InnoDB;
