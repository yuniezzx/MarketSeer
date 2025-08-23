# scripts/init_db.py
from __future__ import annotations
import os
import sys
import mysql.connector
from mysql.connector import errorcode
from utils.config_loader import load_config
from utils.logger import get_data_sources_logger

logger = get_data_sources_logger("scripts.init_db")

SQL_PATH = os.path.join(os.path.dirname(__file__), "scripts", "init_stock_db.sql")

def read_sql_file(path: str) -> str:
    """Read entire SQL file"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_mysql_conn(cfg: dict):
    """Create MySQL connection without selecting database"""
    return mysql.connector.connect(
        host=cfg.get("host", "127.0.0.1"),
        port=cfg.get("port", 3306),
        user=cfg.get("user", "root"),
        password=cfg.get("password", ""),
        autocommit=False,
        use_unicode=True,
        charset="utf8mb4",
        allow_local_infile=True,
    )

def exec_sql_multistatement(conn, sql_text: str):
    """Execute multi-statement SQL atomically"""
    cursor = conn.cursor()
    try:
        # iterate to ensure all statements are sent & all resultsets consumed
        for _ in cursor.execute(sql_text, multi=True):
            pass
        conn.commit()
        logger.info("All statements executed and committed.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Execution failed; rolled back. err={e!r}")
        raise
    finally:
        cursor.close()

def main():
    # 1) load config
    cfg = load_config()              # expects {"mysql": {...}}
    mysql_cfg = cfg.get("mysql") or {}
    if not mysql_cfg:
        logger.error("Missing 'mysql' section in config/settings.yaml")
        sys.exit(1)

    # 2) read SQL
    sql_text = read_sql_file(SQL_PATH)

    # 3) connect & execute
    conn = None
    try:
        conn = get_mysql_conn(mysql_cfg)
        exec_sql_multistatement(conn, sql_text)
        logger.info("✅ Database initialization finished.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger.error("Access denied: check user/password.")
        else:
            logger.error(f"MySQL Error: {err}")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Unexpected error: {e!r}")
        sys.exit(3)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
