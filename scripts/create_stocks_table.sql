-- MarketSeer股票基本信息表
-- 用于存储从各种数据源收集的股票基本信息

CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增',
    symbol VARCHAR(20) NOT NULL UNIQUE COMMENT '股票代码，如000001.SZ',
    name VARCHAR(100) NOT NULL COMMENT '股票名称，如平安银行',
    exchange VARCHAR(20) COMMENT '交易所代码，如SSE/SZSE/HKEX',
    market VARCHAR(50) COMMENT '市场类型，如主板/创业板/科创板',
    industry VARCHAR(100) COMMENT '所属行业',
    sector VARCHAR(100) COMMENT '所属板块',
    list_date DATE COMMENT '上市日期',
    delist_date DATE COMMENT '退市日期，NULL表示未退市',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否活跃交易，1=是，0=否',
    currency VARCHAR(10) DEFAULT 'CNY' COMMENT '交易货币，CNY/USD/HKD等',
    market_cap BIGINT COMMENT '总市值，单位：元',
    shares_outstanding BIGINT COMMENT '流通股数，单位：股',
    description TEXT COMMENT '公司描述',
    website VARCHAR(255) COMMENT '公司官网',
    data_source VARCHAR(20) COMMENT '数据来源，tushare/akshare/yfinance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    
    -- 索引
    INDEX idx_symbol (symbol) COMMENT '股票代码索引',
    INDEX idx_exchange (exchange) COMMENT '交易所索引',
    INDEX idx_industry (industry) COMMENT '行业索引',
    INDEX idx_market (market) COMMENT '市场类型索引',
    INDEX idx_is_active (is_active) COMMENT '活跃状态索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票基本信息表';
