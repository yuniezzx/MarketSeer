"""
pipeline.upsert_stock_basic
实现：从 raw_stock_source 获取原始数据并整理为符合 stock_basic 表字段的 DataFrame（“拿数据”部分）。
"""

from typing import Optional, List, Dict, Any
import json
import pandas as pd
import datetime
import logging
from sqlalchemy import text


from pipeline.helper import get_raw_stock_source
from config.database import engine

logger = logging.getLogger(__name__)

# 依据 schema/stock_basic.sql 定义的主列（尽量覆盖常用列）
STOCK_BASIC_COLUMNS: List[str] = [
    "symbol",
    "name",
    "short_name",
    "full_name",
    "exchange",
    "industry",
    "industry_code",
    "list_date",
    "listed_date",
    "website",
    "total_shares",
    "float_shares",
    "total_market_cap",
    "float_market_cap",
    "net_profit",
    "pe",
    "pb",
    "roe",
    "gross_margin",
    "net_margin",
    "org_id",
    "org_name_cn",
    "org_short_name_cn",
    "org_name_en",
    "main_operation_business",
    "operating_scope",
    "district_encode",
    "org_cn_introduction",
    "legal_representative",
    "general_manager",
    "secretary",
    "established_date",
    "reg_asset",
    "staff_num",
    "telephone",
    "postcode",
    "fax",
    "email",
    "reg_address_cn",
    "office_address_cn",
    "currency",
    "provincial_name",
    "actual_controller",
    "classi_name",
    "pre_name_cn",
    "chairman",
    "executives_nums",
    "actual_issue_vol",
    "issue_price",
    "actual_rc_net_amt",
    "pe_after_issuing",
    "online_success_rate_of_issue",
    "updated_at",
]

# 常见字段映射：源数据字段 -> stock_basic 字段
# 根据常见 akshare/efinance 返回字段做简要映射，后续可扩展
FIELD_MAPPING: Dict[str, str] = {
    # akshare stock_individual_info_em endpoint mapping
    "股票代码": "symbol",
    "股票简称": "short_name",
    "总股本": "total_shares",
    "流通股": "float_shares",
    "总市值": "total_market_cap",
    "流通市值": "float_market_cap",
    "行业": "industry",
    "上市时间": "list_date",
    # akshare stock_individual_basic_info_xq endpoint mapping
    "org_id": "org_id",
    "org_name_cn": "full_name",
    "org_short_name_cn": "org_short_name_cn",
    "org_name_en": "org_name_en",
    "main_operation_business": "main_operation_business",
    "operating_scope": "operating_scope",
    "district_encode": "district_encode",
    "org_cn_introduction": "org_cn_introduction",
    "legal_representative": "legal_representative",
    "general_manager": "general_manager",
    "secretary": "secretary",
    "established_date": "established_date",
    "reg_asset": "reg_asset",
    "staff_num": "staff_num",
    "telephone": "telephone",
    "postcode": "postcode",
    "fax": "fax",
    "email": "email",
    "org_website": "website",
    "reg_address_cn": "reg_address_cn",
    "office_address_cn": "office_address_cn",
    "currency": "currency",
    "provincial_name": "provincial_name",
    "actual_controller": "actual_controller",
    "classi_name": "classi_name",
    "pre_name_cn": "pre_name_cn",
    "chairman": "chairman",
    "executives_nums": "executives_nums",
    "actual_issue_vol": "actual_issue_vol",
    "issue_price": "issue_price",
    "actual_rc_net_amt": "actual_rc_net_amt",
    "pe_after_issuing": "pe_after_issuing",
    "online_success_rate_of_issue": "online_success_rate_of_issue",
    # efinance stock.get_base_info endpoint mapping
    "股票名称": "name",
    "净利润": "net_profit",
    "市盈率(动)": "pe",
    "市净率": "pb",
    "ROE": "roe",
    "毛利率": "gross_margin",
    "净利率": "net_margin",
    "板块编号": "industry_code",
}


def fetch_raw_rows(
    symbol: Optional[str] = None,
    source: Optional[str] = None,
    endpoint: Optional[str] = None,
    since: Optional[int] = None,
    until: Optional[int] = None,
    limit: Optional[int] = None,
    as_df: bool = True,
):
    """
    从 raw_stock_source 拉取原始行，返回 DataFrame（默认）或 list[dict]。
    仅负责读取 raw 表，不做解析。
    """
    return get_raw_stock_source(
        symbol=symbol, source=source, endpoint=endpoint, since=since, until=until, limit=limit, as_df=as_df
    )


def get_exchange(symbol: str) -> str:
    # 上海证券交易所
    if symbol.startswith(('600', '601', '603', '605')):
        return 'SSE'  # 上交所
    # 深圳证券交易所
    elif symbol.startswith(('000', '001', '002', '003', '004')):
        return 'SZSE'  # 深交所
    # 北京证券交易所
    elif symbol.startswith(('430', '831', '833', '839', '870', '871', '872', '873')):
        return 'BSE'  # 北交所
    else:
        logger.warning(f"Unknown exchange pattern for symbol: {symbol}")
        return ''


def upsert_stock_basic(symbol: str) -> Dict[str, Any]:
    """
    从raw_stock_source获取指定symbol的三个数据源，整理后写入stock_basic表
    Args:
        symbol: 股票代码
    Returns:
        整理后的股票数据字典
    """
    # 1. 获取三个数据源的最新数据
    sources = [
        ("akshare", "stock_individual_info_em"),
        ("akshare", "stock_individual_basic_info_xq"),
        ("efinance", "stock.get_base_info"),
    ]

    merged_data = {}

    # 添加交易所信息
    merged_data['exchange'] = get_exchange(symbol)

    for source, endpoint in sources:
        raw_df = fetch_raw_rows(symbol=symbol, source=source, endpoint=endpoint)
        if raw_df.empty:
            logger.warning(f"No data found for {symbol} from {source}.{endpoint}")
            continue

        # 解析JSON数据
        raw_data = json.loads(raw_df.iloc[-1]["raw"])  # 使用最新的一条记录

        # 如果raw_data是列表（akshare格式），转换为字典
        if isinstance(raw_data, list):
            raw_data = {item["item"]: item["value"] for item in raw_data}

        # 使用FIELD_MAPPING映射字段，但仅保留STOCK_BASIC_COLUMNS中定义的字段
        for src_field, dest_field in FIELD_MAPPING.items():
            if src_field in raw_data and dest_field in STOCK_BASIC_COLUMNS:
                merged_data[dest_field] = raw_data[src_field]

    # 确保必需字段存在
    if "symbol" not in merged_data:
        merged_data["symbol"] = symbol

    # 添加更新时间
    merged_data["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 处理特殊字段
    if "listed_date" in merged_data:
        # 将上市日期转换为时间戳
        try:
            listed_date = str(merged_data["list_date"])
            listed_date = datetime.datetime.strptime(listed_date, "%Y%m%d").timestamp()
            merged_data["listed_date"] = int(listed_date)
        except Exception as e:
            logger.warning(f"Failed to parse listed_date for {symbol}: {e}")

    if "established_date" in merged_data:
        # 确保established_date是整数类型
        try:
            merged_data["established_date"] = int(merged_data["established_date"]) // 1000  # 转换为秒级时间戳
        except Exception as e:
            logger.warning(f"Failed to convert established_date for {symbol}: {e}")

    # 构建要插入的列和值，确保只包含STOCK_BASIC_COLUMNS中定义的字段
    columns = []
    values = []
    params = {}

    # 从merged_data中移除任何不在STOCK_BASIC_COLUMNS中的字段
    merged_data = {k: v for k, v in merged_data.items() if k in STOCK_BASIC_COLUMNS}

    # 仅包含在STOCK_BASIC_COLUMNS中定义的字段
    for col in STOCK_BASIC_COLUMNS:
        if col in merged_data:
            columns.append(col)
            values.append(f":{col}")
            params[col] = merged_data[col]

    # 构建UPSERT SQL语句
    sql = f"""
    INSERT OR REPLACE INTO stock_basic ({', '.join(columns)})
    VALUES ({', '.join(values)})
    """

    # 执行SQL
    try:
        with engine.connect() as conn:
            conn.execute(text(sql), params)
            conn.commit()
            logger.info(f"Successfully upserted stock_basic data for symbol {symbol}")
    except Exception as e:
        logger.error(f"Failed to upsert stock_basic data for symbol {symbol}: {e}")
        raise

    return merged_data


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python upsert_stock_basic.py <symbol>")
        print("Example: python upsert_stock_basic.py 002104")
        sys.exit(1)

    symbol = sys.argv[1]
    try:
        result = upsert_stock_basic(symbol)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error processing symbol {symbol}: {e}", file=sys.stderr)
        sys.exit(1)
