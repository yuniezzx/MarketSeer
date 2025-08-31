"""
数据类型定义

定义数据收集模块中使用的数据结构和类型。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import pandas as pd


@dataclass
class DataCollectorConfig:
    """数据收集器配置"""

    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    rate_limit_delay: float = 1.0
    token: Optional[str] = None
    proxy: Optional[Dict[str, str]] = None
    custom_headers: Optional[Dict[str, str]] = None


@dataclass
class StockInfo:
    """股票基本信息"""

    symbol: str  # 股票代码
    name: str  # 股票名称
    exchange: str  # 交易所
    market: str  # 市场类型 (主板/创业板/科创板等)
    industry: Optional[str] = None  # 行业
    sector: Optional[str] = None  # 板块
    list_date: Optional[date] = None  # 上市日期
    delist_date: Optional[date] = None  # 退市日期
    is_active: bool = True  # 是否活跃交易
    currency: str = 'CNY'  # 货币类型
    market_cap: Optional[float] = None  # 市值
    shares_outstanding: Optional[float] = None  # 流通股数
    description: Optional[str] = None  # 公司描述
    website: Optional[str] = None  # 公司网站
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据


@dataclass
class HistoricalData:
    """历史行情数据"""

    symbol: str  # 股票代码
    date: date  # 交易日期
    open: Optional[float] = None  # 开盘价
    high: Optional[float] = None  # 最高价
    low: Optional[float] = None  # 最低价
    close: Optional[float] = None  # 收盘价
    volume: Optional[float] = None  # 成交量
    amount: Optional[float] = None  # 成交额
    turnover_rate: Optional[float] = None  # 换手率
    pe_ratio: Optional[float] = None  # 市盈率
    pb_ratio: Optional[float] = None  # 市净率
    adj_close: Optional[float] = None  # 复权收盘价
    pre_close: Optional[float] = None  # 前收盘价
    change: Optional[float] = None  # 涨跌额
    pct_change: Optional[float] = None  # 涨跌幅(%)
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'symbol': self.symbol,
            'date': self.date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount,
            'turnover_rate': self.turnover_rate,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'adj_close': self.adj_close,
            'pre_close': self.pre_close,
            'change': self.change,
            'pct_change': self.pct_change,
            **self.metadata,
        }


@dataclass
class RealtimeData:
    """实时行情数据"""

    symbol: str  # 股票代码
    name: str  # 股票名称
    timestamp: datetime  # 数据时间戳
    current_price: Optional[float] = None  # 当前价格
    open: Optional[float] = None  # 开盘价
    high: Optional[float] = None  # 最高价
    low: Optional[float] = None  # 最低价
    pre_close: Optional[float] = None  # 前收盘价
    volume: Optional[float] = None  # 成交量
    amount: Optional[float] = None  # 成交额
    change: Optional[float] = None  # 涨跌额
    pct_change: Optional[float] = None  # 涨跌幅(%)
    bid_price: Optional[float] = None  # 买一价
    ask_price: Optional[float] = None  # 卖一价
    bid_volume: Optional[float] = None  # 买一量
    ask_volume: Optional[float] = None  # 卖一量
    bid_prices: List[float] = field(default_factory=list)  # 买盘价格(5档)
    ask_prices: List[float] = field(default_factory=list)  # 卖盘价格(5档)
    bid_volumes: List[float] = field(default_factory=list)  # 买盘数量(5档)
    ask_volumes: List[float] = field(default_factory=list)  # 卖盘数量(5档)
    turnover_rate: Optional[float] = None  # 换手率
    pe_ratio: Optional[float] = None  # 市盈率
    pb_ratio: Optional[float] = None  # 市净率
    market_cap: Optional[float] = None  # 总市值
    circulation_market_cap: Optional[float] = None  # 流通市值
    status: str = 'trading'  # 交易状态 (trading/suspended/delisted)
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'timestamp': self.timestamp,
            'current_price': self.current_price,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'pre_close': self.pre_close,
            'volume': self.volume,
            'amount': self.amount,
            'change': self.change,
            'pct_change': self.pct_change,
            'bid_price': self.bid_price,
            'ask_price': self.ask_price,
            'bid_volume': self.bid_volume,
            'ask_volume': self.ask_volume,
            'bid_prices': self.bid_prices,
            'ask_prices': self.ask_prices,
            'bid_volumes': self.bid_volumes,
            'ask_volumes': self.ask_volumes,
            'turnover_rate': self.turnover_rate,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'market_cap': self.market_cap,
            'circulation_market_cap': self.circulation_market_cap,
            'status': self.status,
            **self.metadata,
        }


@dataclass
class FinancialData:
    """财务数据"""

    symbol: str  # 股票代码
    report_date: date  # 报告期
    ann_date: Optional[date] = None  # 公告日期

    # 资产负债表数据
    total_assets: Optional[float] = None  # 总资产
    total_liabilities: Optional[float] = None  # 总负债
    total_equity: Optional[float] = None  # 总股东权益
    current_assets: Optional[float] = None  # 流动资产
    current_liabilities: Optional[float] = None  # 流动负债

    # 利润表数据
    total_revenue: Optional[float] = None  # 营业总收入
    net_profit: Optional[float] = None  # 净利润
    operating_profit: Optional[float] = None  # 营业利润
    gross_profit: Optional[float] = None  # 毛利润
    operating_expense: Optional[float] = None  # 营业费用

    # 现金流量表数据
    net_cash_flow_operating: Optional[float] = None  # 经营活动现金流量净额
    net_cash_flow_investing: Optional[float] = None  # 投资活动现金流量净额
    net_cash_flow_financing: Optional[float] = None  # 筹资活动现金流量净额

    # 财务指标
    eps: Optional[float] = None  # 每股收益
    bvps: Optional[float] = None  # 每股净资产
    roe: Optional[float] = None  # 净资产收益率
    roa: Optional[float] = None  # 总资产收益率
    debt_to_equity: Optional[float] = None  # 资产负债率
    current_ratio: Optional[float] = None  # 流动比率
    quick_ratio: Optional[float] = None  # 速动比率
    gross_margin: Optional[float] = None  # 毛利率
    net_margin: Optional[float] = None  # 净利率

    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'symbol': self.symbol,
            'report_date': self.report_date,
            'ann_date': self.ann_date,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'total_equity': self.total_equity,
            'current_assets': self.current_assets,
            'current_liabilities': self.current_liabilities,
            'total_revenue': self.total_revenue,
            'net_profit': self.net_profit,
            'operating_profit': self.operating_profit,
            'gross_profit': self.gross_profit,
            'operating_expense': self.operating_expense,
            'net_cash_flow_operating': self.net_cash_flow_operating,
            'net_cash_flow_investing': self.net_cash_flow_investing,
            'net_cash_flow_financing': self.net_cash_flow_financing,
            'eps': self.eps,
            'bvps': self.bvps,
            'roe': self.roe,
            'roa': self.roa,
            'debt_to_equity': self.debt_to_equity,
            'current_ratio': self.current_ratio,
            'quick_ratio': self.quick_ratio,
            'gross_margin': self.gross_margin,
            'net_margin': self.net_margin,
            **self.metadata,
        }


# 类型别名
StockSymbol = str
DateRange = tuple[Union[str, date], Union[str, date]]
DataFrameType = pd.DataFrame
