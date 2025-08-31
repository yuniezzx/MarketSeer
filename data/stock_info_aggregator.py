# Aggregator to merge data from Efinance and Akshare clients and upsert into DB using SQLAlchemy ORM
#
# Usage:
#   from data.stock_info_aggregator import StockInfoAggregator
#   from sqlalchemy.orm import Session
#
#   agg = StockInfoAggregator()
#   result = agg.aggregate_and_upsert("600519", session)  # session is SQLAlchemy Session
#
# Result: returns a dict containing 'symbol' and 'missing_fields'

from typing import Any, Dict, List, Optional, Sequence, Iterable
from decimal import Decimal
from sqlalchemy.orm import Session
from models.stock import StockInfo
from data.efinance_client import EfinanceClient
from data.akshare_client import AkshareClient

# Local DB session factory (used when caller does not provide a session)
from config.database import SessionLocal  # type: ignore


# Lightweight helpers for extracting values from heterogeneous raw results
def _to_dict(raw: Any) -> Dict[str, Any]:
    try:
        # pandas DataFrame/Series support
        import pandas as _pd  # type: ignore
    except Exception:
        _pd = None  # type: ignore

    if _pd is not None:
        if hasattr(raw, "to_dict") and not isinstance(raw, dict):
            try:
                return raw.to_dict()
            except Exception:
                pass
        # DataFrame -> first record
        if hasattr(raw, "iterrows"):
            try:
                for _, row in raw.iterrows():
                    return row.to_dict()
            except Exception:
                pass
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, (list, tuple)) and raw:
        if isinstance(raw[0], dict):
            return dict(raw[0])
    # fallback: cannot convert
    return {}


def _pick_from(raw: Dict[str, Any], candidates: Sequence[str]) -> Optional[Any]:
    if not raw:
        return None
    for k in candidates:
        if k in raw and raw[k] not in (None, ""):
            return raw[k]
    # case-insensitive
    lowered = {str(k).strip().lower(): v for k, v in raw.items() if isinstance(k, str)}
    for k in candidates:
        key = str(k).strip().lower()
        if key in lowered and lowered[key] not in (None, ""):
            return lowered[key]
    return None


def _infer_market_from_code(code: str) -> Optional[str]:
    # Simple heuristic for China A-shares
    if not code or not code.isdigit():
        return None
    if code.startswith(("6", "9")):
        return "SH"
    if code.startswith(("0", "3", "2", "1")):
        return "SZ"
    return None


class StockInfoAggregator:
    def __init__(self) -> None:
        self.ef = EfinanceClient()
        self.ak = AkshareClient()

    def _collect_sources(self, code_or_symbol: str) -> List[Dict[str, Any]]:
        sources: List[Dict[str, Any]] = []
        # efinance raw
        try:
            raw_ef = self.ef.stock_individual_info_ef(code_or_symbol)
            sources.append(_to_dict(raw_ef))
        except Exception:
            sources.append({})
        # akshare EM (may return mapped dict or raw)
        try:
            raw_em = self.ak.stock_individual_info_em(code_or_symbol)
            sources.append(_to_dict(raw_em))
        except Exception:
            sources.append({})
        # akshare XQ
        try:
            raw_xq = self.ak.stock_individual_basic_info_xq(code_or_symbol)
            sources.append(_to_dict(raw_xq))
        except Exception:
            sources.append({})
        return sources

    def aggregate(self, code_or_symbol: str) -> Dict[str, Any]:
        """
        Merge data from efinance / akshare_em / akshare_xq into a single dict of StockInfo fields.
        This function does NOT persist to DB.
        Returns dict of candidate fields (missing fields will be absent or set to None).
        """
        sources = self._collect_sources(code_or_symbol)
        ef_raw, em_raw, xq_raw = sources[0], sources[1], sources[2]

        # candidate keys for each StockInfo attribute (ordered by preference when searching a single raw dict)
        key_candidates: Dict[str, List[str]] = {
            "symbol": ["symbol", "code", "股票代码", "股票代码(后缀)", "stock_code"],
            "code": ["code", "股票代码", "股票代码(纯数字)", "stock_code"],
            "market": ["market", "交易所", "exchange"],
            "name": ["name", "股票名称", "简称", "stock_name", "股票简称"],
            "full_name": ["full_name", "公司全称", "org_name_cn", "org_name", "name_full"],
            "english_name": ["english_name", "org_name_en"],
            "industry": ["industry", "所属行业", "行业", "所处行业"],
            "sector": ["sector", "板块", "板块编号", "板块代码"],
            "concept": ["concept", "概念", "概念板块"],
            "isin": ["isin", "ISIN"],
            "delist_date": ["退市日期", "delist_date"],
            "company_type": ["company_type", "classi_name", "公司类型"],
            "legal_representative": ["legal_representative", "法人"],
            "registered_capital": ["registered_capital", "reg_asset", "注册资本"],
            "establishment_date": ["establishment_date", "established_date", "成立日期"],
            "listing_date": ["listing_date", "上市时间", "listed_date", "上市日期"],
            "province": ["province", "provincial_name", "省份"],
            "city": ["city"],
            "address": ["address", "reg_address_cn", "office_address_cn", "注册地址"],
            "website": ["website", "org_website", "公司网址"],
            "business_scope": ["business_scope", "operating_scope", "经营范围"],
            "main_business": ["main_business", "main_operation_business", "org_cn_introduction", "主营业务"],
            "total_shares": ["total_shares", "总股本", "总股本(股)", "actual_issue_vol"],
            "circulating_shares": ["circulating_shares", "流通股", "流通股本", "流通股(股)"],
            "free_float_shares": ["free_float_shares", "自由流通股", "流通A股"],
            "market_cap": ["market_cap", "总市值", "总市值(元)", "market_value"],
            "circulating_market_cap": ["circulating_market_cap", "流通市值", "流通市值(元)"],
            "pe_ratio": ["pe_ratio", "市盈率(动)", "市盈率", "PE"],
            "pb_ratio": ["pb_ratio", "市净率", "PB"],
            "eps": ["eps", "每股收益", "每股收益(元)"],
            "bps": ["bps", "每股净资产", "每股净资产(元)"],
            "roe": ["roe", "ROE", "净资产收益率"],
            "debt_ratio": ["debt_ratio", "资产负债率"],
            "status": ["status", "交易状态", "trade_status"],
            "is_st": ["is_st", "是否ST"],
            "currency": ["currency", "币种", "货币"],
            "lot_size": ["lot_size", "最小交易单位", "每手"],
            "latest_price": [
                "latest_price",
                "最新价",
                "close",
                "最新收盘价",
                "now",
                "current",
                "price",
                "最新价(元)",
            ],
            "turnover_rate": ["turnover_rate", "换手率"],
            "volume": ["volume", "成交量", "成交量(股)"],
            "description": ["description", "公司简介", "org_cn_introduction", "简介"],
            "remarks": ["remarks", "备注"],
        }

        merged: Dict[str, Any] = {}

        # Search order of sources: efinance -> akshare EM -> akshare XQ
        for target, keys in key_candidates.items():
            val = None
            for src in (ef_raw, em_raw, xq_raw):
                val = _pick_from(src, keys)
                if val is not None:
                    merged[target] = val
                    break
            if val is None:
                merged[target] = None

        # Normalize symbol/code/market
        code = merged.get("code") or (
            code_or_symbol.split(".")[0] if "." in code_or_symbol else code_or_symbol
        )
        if code:
            merged["code"] = str(code)
        market = merged.get("market")
        if not market:
            inferred = _infer_market_from_code(str(code)) if code else None
            if inferred:
                merged["market"] = inferred
        # Ensure symbol contains market suffix if possible
        if merged.get("symbol"):
            sym = str(merged["symbol"])
            if "." not in sym and merged.get("market"):
                merged["symbol"] = f"{sym}.{merged['market']}"
        else:
            # construct symbol from code + market if possible
            if merged.get("code") and merged.get("market"):
                merged["symbol"] = f"{merged['code']}.{merged['market']}"
            elif merged.get("code"):
                merged["symbol"] = merged["code"]

        # Normalize date-like fields (ensure SQLAlchemy Date columns get Python date objects)
        from datetime import datetime, date as _date

        def _to_date(val):
            try:
                if val is None:
                    return None
                if isinstance(val, _date):
                    return val
                if isinstance(val, int):
                    s = str(val)
                    # yyyymmdd
                    if len(s) == 8:
                        return _date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
                    # epoch seconds or milliseconds
                    ts = int(val)
                    if ts > 1e11:  # milliseconds
                        ts = ts / 1000.0
                    return datetime.fromtimestamp(ts).date()
                if isinstance(val, float):
                    # treat as timestamp seconds
                    ts = float(val)
                    if ts > 1e11:
                        ts = ts / 1000.0
                    return datetime.fromtimestamp(ts).date()
                if isinstance(val, str):
                    s = val.strip()
                    if s.isdigit() and len(s) == 8:
                        return _date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
                    # ISO formats
                    try:
                        return datetime.fromisoformat(s).date()
                    except Exception:
                        pass
                    # try parsing as int timestamp string
                    if s.isdigit():
                        ts = int(s)
                        if ts > 1e11:
                            ts = ts / 1000.0
                        return datetime.fromtimestamp(ts).date()
            except Exception:
                pass
            return None

        for _d in ("listing_date", "establishment_date"):
            v = merged.get(_d)
            if v not in (None, ""):
                dt = _to_date(v)
                if dt is not None:
                    merged[_d] = dt

        return merged

    def aggregate_and_upsert(self, code_or_symbol: str, session: Session) -> Dict[str, Any]:
        """
        Aggregate data and upsert into DB using SQLAlchemy session.
        Returns dict { "symbol": ..., "missing_fields": [...] }
        Commits the session.
        """
        merged = self.aggregate(code_or_symbol)
        symbol = merged.get("symbol")
        if not symbol:
            # cannot upsert without symbol; raise
            raise RuntimeError(
                "无法确定 symbol，无法写入数据库。请提供带后缀的 symbol 或确保数据源返回代码/交易所信息。"
            )

        # prepare payload only for columns present in StockInfo model
        payload: Dict[str, Any] = {}
        # list of StockInfo fields we will attempt to write
        fields = [
            "symbol",
            "code",
            "market",
            "name",
            "full_name",
            "english_name",
            "industry",
            "sector",
            "concept",
            "isin",
            "delist_date",
            "company_type",
            "legal_representative",
            "registered_capital",
            "establishment_date",
            "listing_date",
            "province",
            "city",
            "address",
            "website",
            "business_scope",
            "main_business",
            "total_shares",
            "circulating_shares",
            "market_cap",
            "circulating_market_cap",
            "pe_ratio",
            "pb_ratio",
            "eps",
            "bps",
            "roe",
            "debt_ratio",
            "status",
            "is_st",
            "currency",
            "lot_size",
            "description",
            "remarks",
        ]
        for f in fields:
            v = merged.get(f)
            if v is not None:
                payload[f] = v

        # upsert via primary key (symbol)
        existing = session.get(StockInfo, symbol)
        if existing is None:
            # create new
            obj = StockInfo(**{k: payload.get(k) for k in fields if k in payload})
            session.add(obj)
        else:
            # update existing fields
            for k, v in payload.items():
                setattr(existing, k, v)
            obj = existing

        # set last_sync_time
        try:
            from datetime import datetime

            obj.last_sync_time = datetime.now()
        except Exception:
            pass

        session.commit()

        # determine missing fields (those that remain None in merged for model fields)
        missing = [f for f in fields if merged.get(f) is None]

        return {"symbol": symbol, "missing_fields": missing}

    def aggregate_and_upsert_many(
        self,
        codes: Iterable[str],
        session: Optional[Session] = None,
        chunk_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Batch-aggregate and upsert a list of stock codes (pure numeric codes, e.g., '600519').
        - codes: iterable of codes (strings)
        - session: optional SQLAlchemy Session; if not provided, a SessionLocal will be used
        - chunk_size: how many records to commit per transaction

        Returns summary dict:
        {
            "total": int,
            "succeeded": int,
            "failed": int,
            "results": [ { "code": ..., "symbol": ..., "missing_fields": [...], "error": Optional[str] }, ... ]
        }
        """
        own_session = False
        if session is None:
            session = SessionLocal()
            own_session = True

        total = 0
        succeeded = 0
        failed = 0
        results: List[Dict[str, Any]] = []

        buffer_count = 0
        try:
            for code in codes:
                total += 1
                try:
                    merged = self.aggregate(code)
                    # prepare payload same as aggregate_and_upsert but without committing per record
                    payload: Dict[str, Any] = {}
                    fields = [
                        "symbol",
                        "code",
                        "market",
                        "name",
                        "full_name",
                        "english_name",
                        "industry",
                        "sector",
                        "concept",
                        "isin",
                        "delist_date",
                        "company_type",
                        "legal_representative",
                        "registered_capital",
                        "establishment_date",
                        "listing_date",
                        "province",
                        "city",
                        "address",
                        "website",
                        "business_scope",
                        "main_business",
                        "total_shares",
                        "circulating_shares",
                        "market_cap",
                        "circulating_market_cap",
                        "pe_ratio",
                        "pb_ratio",
                        "eps",
                        "bps",
                        "roe",
                        "debt_ratio",
                        "status",
                        "is_st",
                        "currency",
                        "lot_size",
                        "description",
                        "remarks",
                    ]
                    for f in fields:
                        v = merged.get(f)
                        if v is not None:
                            payload[f] = v

                    symbol = payload.get("symbol")
                    if not symbol:
                        raise RuntimeError("无法确定 symbol，跳过此条写入。")

                    existing = session.get(StockInfo, symbol)
                    if existing is None:
                        obj = StockInfo(**{k: payload.get(k) for k in fields if k in payload})
                        session.add(obj)
                    else:
                        for k, v in payload.items():
                            setattr(existing, k, v)
                        obj = existing

                    # update last_sync_time on object
                    try:
                        from datetime import datetime

                        obj.last_sync_time = datetime.now()
                    except Exception:
                        pass

                    buffer_count += 1
                    if buffer_count >= chunk_size:
                        session.commit()
                        buffer_count = 0

                    succeeded += 1
                    results.append(
                        {
                            "code": code,
                            "symbol": symbol,
                            "missing_fields": [f for f in fields if merged.get(f) is None],
                            "error": None,
                        }
                    )
                except Exception as e:
                    failed += 1
                    results.append({"code": code, "symbol": None, "missing_fields": [], "error": str(e)})
                    # continue with next code
            # final commit for leftover buffer
            if buffer_count > 0:
                session.commit()
        finally:
            if own_session and session is not None:
                session.close()

        return {"total": total, "succeeded": succeeded, "failed": failed, "results": results}
