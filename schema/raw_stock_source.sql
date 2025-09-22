-- schema/raw_stock_source.sql
-- DDL + common DML examples for raw_stock_source table
-- 用途：归档数据客户端的原始响应（JSON/text）
-- 该文件只包含 SQL，可直接用于 sqlite 执行或作为迁移脚本的一部分

-- CREATE TABLE (幂等)
CREATE TABLE IF NOT EXISTS raw_stock_source (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  symbol TEXT,
  source TEXT,
  endpoint TEXT,
  raw TEXT,
  fetched_at INTEGER
);

-- INDEX (加速按 symbol 查询；非唯一，因为同一 symbol 可有多条归档记录)
CREATE INDEX IF NOT EXISTS idx_raw_symbol ON raw_stock_source(symbol);

-- 常用 INSERT（参数化，推荐用于 SQLAlchemy text() 或其他支持命名参数的库）
-- 使用示例（SQLAlchemy）：
-- conn.execute(text("INSERT INTO raw_stock_source (symbol, source, endpoint, raw, fetched_at) VALUES (:symbol, :source, :endpoint, :raw, :fetched_at)"),
--              {"symbol": symbol, "source": source, "endpoint": endpoint, "raw": raw_text, "fetched_at": fetched_at})

INSERT INTO raw_stock_source (symbol, source, endpoint, raw, fetched_at)
VALUES (:symbol, :source, :endpoint, :raw, :fetched_at);

-- 备用：sqlite3 原生占位符（用于 sqlite3 库的 execute）
-- INSERT INTO raw_stock_source (symbol, source, endpoint, raw, fetched_at)
-- VALUES (?, ?, ?, ?, ?);
