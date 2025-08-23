# scripts/init_db.py
from __future__ import annotations
import sys
import mysql.connector
from mysql.connector import errorcode
from utils.config_loader import load_config
from utils.logger import get_data_sources_logger

logger = get_data_sources_logger("scripts.init_db")

INIT_DB_PATH = "db/init_stock_db.sql"

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

def exec_sql(conn, sql_text: str):
    """Execute multi-statement SQL atomically (manual split, no `multi=True`)"""
    cursor = conn.cursor()
    try:
        # 手动按分号切分语句
        for statement in sql_text.split(";"):
            stmt = statement.strip()
            if stmt:  # 忽略空语句
                cursor.execute(stmt)
        conn.commit()
        logger.info("All statements executed and committed.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Execution failed; rolled back. err={e!r}")
        raise
    finally:
        cursor.close()


def init_stock_db():
    # 1) load config
    cfg = load_config()
    database_cfg = cfg.get("database") or {}
    local_db_cfg = database_cfg.get("local_db") or {}
    print(local_db_cfg)
    if not local_db_cfg:
        logger.error("Missing 'mysql' section in config/settings.yaml")
        sys.exit(1)

    # 2) read SQL
    sql_text = read_sql_file(INIT_DB_PATH)

    # 3) connect & execute
    conn = None
    try:
        conn = get_mysql_conn(local_db_cfg)
        exec_sql(conn, sql_text)
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

def main():
    init_stock_db()

if __name__ == "__main__":
    main()
