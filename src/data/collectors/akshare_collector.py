"""
AKShare数据收集器

提供AKShare数据源的统一接口，支持：
- 中国A股数据
- 港股数据
- 美股数据
- 期货数据
- 基金数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import time

from .base_collector import BaseCollector
from .data_types import StockInfo, HistoricalData, RealtimeData, FinancialData
from .exceptions import (
    DataCollectorError,
    APIError,
    DataNotAvailableError,
    SymbolNotFoundError,
    ValidationError,
    RateLimitError,
)


class AKShareCollector(BaseCollector):
    """AKShare数据收集器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化AKShare收集器

        Args:
            config: 配置字典，可选
        """
        super().__init__("akshare", config)
        self.source = "akshare"
        # 从配置中获取速率限制延迟，处理不同的配置类型
        if hasattr(self.config, 'get'):
            self.rate_limit_delay = self.config.get('rate_limit_delay', 1.0)
        elif hasattr(self.config, 'rate_limit_delay'):
            self.rate_limit_delay = getattr(self.config, 'rate_limit_delay', 1.0)
        else:
            self.rate_limit_delay = 1.0  # 默认值

    def _rate_limit(self):
        """执行速率限制"""
        if hasattr(self, '_last_request_time'):
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _normalize_symbol(self, symbol: str) -> str:
        """
        规范化股票代码

        Args:
            symbol: 原始股票代码

        Returns:
            str: 规范化后的股票代码
        """
        symbol = symbol.upper().strip()

        # 处理A股代码
        if len(symbol) == 6 and symbol.isdigit():
            # 根据代码范围判断交易所
            code_num = int(symbol)
            if code_num >= 600000 and code_num <= 688999:
                return symbol  # 上海A股
            elif code_num >= 000000 and code_num <= 399999:
                return symbol  # 深圳A股
            elif code_num >= 400000 and code_num <= 499999:
                return symbol  # 三板
            elif code_num >= 830000 and code_num <= 899999:
                return symbol  # 北交所

        # 处理港股代码
        if symbol.endswith('.HK') or (len(symbol) <= 5 and symbol.isdigit()):
            return symbol.replace('.HK', '')

        # 处理美股代码
        if len(symbol) <= 5 and symbol.isalpha():
            return symbol

        return symbol

    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            StockInfo: 股票信息对象，如果获取失败返回None

        Raises:
            SymbolNotFoundError: 股票代码不存在
            APIError: API调用失败
        """
        try:
            self._rate_limit()
            normalized_symbol = self._normalize_symbol(symbol)

            # 尝试获取A股信息
            try:
                # 获取股票基本信息
                stock_info_df = ak.stock_individual_info_em(symbol=normalized_symbol)
                if stock_info_df.empty:
                    raise SymbolNotFoundError(f"股票代码 {symbol} 不存在")

                # 提取基本信息
                info_dict = {}
                for _, row in stock_info_df.iterrows():
                    info_dict[row['item']] = row['value']

                return StockInfo(
                    symbol=normalized_symbol,
                    name=info_dict.get('股票简称', ''),
                    exchange=self._get_exchange_from_symbol(normalized_symbol),
                    currency='CNY',
                    sector=info_dict.get('所属行业', ''),
                    market_cap=self._parse_market_cap(info_dict.get('总市值', '')),
                    shares_outstanding=self._parse_shares(info_dict.get('流通股本', '')),
                    last_updated=datetime.now(),
                )

            except Exception as e:
                # 如果A股信息获取失败，尝试其他市场
                self.logger.warning(f"获取A股信息失败，尝试其他市场: {e}")

                # 尝试港股
                try:
                    hk_info = ak.stock_hk_spot_em()
                    hk_stock = hk_info[hk_info['代码'] == normalized_symbol]
                    if not hk_stock.empty:
                        row = hk_stock.iloc[0]
                        return StockInfo(
                            symbol=normalized_symbol,
                            name=row['名称'],
                            exchange='HKEX',
                            currency='HKD',
                            sector='',
                            market_cap=None,
                            shares_outstanding=None,
                            last_updated=datetime.now(),
                        )
                except Exception:
                    pass

                raise SymbolNotFoundError(f"未找到股票代码 {symbol} 的信息")

        except Exception as e:
            self._update_stats('error')
            if isinstance(e, (SymbolNotFoundError, DataCollectorError)):
                raise
            raise APIError(f"AKShare API调用失败: {str(e)}")

    def get_historical_data(
        self, symbol: str, start_date: str, end_date: str, period: str = 'daily', adjust: str = 'qfq'
    ) -> List[HistoricalData]:
        """
        获取历史数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 数据周期 ('daily', 'weekly', 'monthly')
            adjust: 复权类型 ('qfq'-前复权, 'hfq'-后复权, ''-不复权)

        Returns:
            List[HistoricalData]: 历史数据列表
        """
        try:
            self._rate_limit()
            normalized_symbol = self._normalize_symbol(symbol)

            # 转换日期格式
            start_date_formatted = self._format_date_for_akshare(start_date)
            end_date_formatted = self._format_date_for_akshare(end_date)

            # 根据周期选择不同的接口
            if period == 'daily':
                if adjust == 'qfq':
                    df = ak.stock_zh_a_hist(
                        symbol=normalized_symbol,
                        start_date=start_date_formatted,
                        end_date=end_date_formatted,
                        adjust="qfq",
                    )
                elif adjust == 'hfq':
                    df = ak.stock_zh_a_hist(
                        symbol=normalized_symbol,
                        start_date=start_date_formatted,
                        end_date=end_date_formatted,
                        adjust="hfq",
                    )
                else:
                    df = ak.stock_zh_a_hist(
                        symbol=normalized_symbol,
                        start_date=start_date_formatted,
                        end_date=end_date_formatted,
                        adjust="",
                    )
            else:
                raise ValidationError(f"不支持的数据周期: {period}")

            if df.empty:
                return []

            # 转换数据格式
            historical_data = []
            for _, row in df.iterrows():
                data = HistoricalData(
                    symbol=normalized_symbol,
                    date=pd.to_datetime(row['日期']).date(),
                    open=float(row['开盘']),
                    high=float(row['最高']),
                    low=float(row['最低']),
                    close=float(row['收盘']),
                    volume=int(row['成交量']) if pd.notna(row['成交量']) else 0,
                    amount=float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                    change=float(row['涨跌幅']) if '涨跌幅' in row and pd.notna(row['涨跌幅']) else 0.0,
                    change_pct=float(row['涨跌幅']) if '涨跌幅' in row and pd.notna(row['涨跌幅']) else 0.0,
                    turnover=0.0,  # AKShare 基础接口不提供换手率
                    last_updated=datetime.now(),
                )
                historical_data.append(data)

            self._update_stats('success')
            return historical_data

        except Exception as e:
            self._update_stats('error')
            if isinstance(e, DataCollectorError):
                raise
            raise APIError(f"获取历史数据失败: {str(e)}")

    def get_realtime_data(self, symbol: str) -> Optional[RealtimeData]:
        """
        获取实时数据

        Args:
            symbol: 股票代码

        Returns:
            RealtimeData: 实时数据对象
        """
        try:
            self._rate_limit()
            normalized_symbol = self._normalize_symbol(symbol)

            # 获取实时行情
            realtime_df = ak.stock_zh_a_spot_em()
            stock_data = realtime_df[realtime_df['代码'] == normalized_symbol]

            if stock_data.empty:
                raise SymbolNotFoundError(f"未找到股票代码 {symbol} 的实时数据")

            row = stock_data.iloc[0]

            realtime_data = RealtimeData(
                symbol=normalized_symbol,
                current_price=float(row['最新价']),
                open_price=float(row['今开']),
                high_price=float(row['最高']),
                low_price=float(row['最低']),
                previous_close=float(row['昨收']),
                volume=int(row['成交量']),
                amount=float(row['成交额']),
                change=float(row['涨跌额']),
                change_pct=float(row['涨跌幅']),
                turnover=float(row['换手率']) if '换手率' in row and pd.notna(row['换手率']) else 0.0,
                timestamp=datetime.now(),
                last_updated=datetime.now(),
            )

            self._update_stats('success')
            return realtime_data

        except Exception as e:
            self._update_stats('error')
            if isinstance(e, DataCollectorError):
                raise
            raise APIError(f"获取实时数据失败: {str(e)}")

    def get_financial_data(self, symbol: str, report_type: str = 'annual') -> List[FinancialData]:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            report_type: 报告类型 ('annual', 'quarterly')

        Returns:
            List[FinancialData]: 财务数据列表
        """
        try:
            self._rate_limit()
            normalized_symbol = self._normalize_symbol(symbol)

            financial_data_list = []

            # 获取利润表数据
            try:
                profit_df = ak.stock_financial_analysis_indicator(symbol=normalized_symbol)
                if not profit_df.empty:
                    for _, row in profit_df.iterrows():
                        try:
                            financial_data = FinancialData(
                                symbol=normalized_symbol,
                                report_date=pd.to_datetime(row['日期']).date(),
                                report_type=report_type,
                                revenue=self._safe_float(row.get('营业总收入', 0)),
                                net_income=self._safe_float(row.get('净利润', 0)),
                                total_assets=self._safe_float(row.get('总资产', 0)),
                                total_equity=self._safe_float(row.get('股东权益合计', 0)),
                                eps=self._safe_float(row.get('基本每股收益', 0)),
                                roe=self._safe_float(row.get('净资产收益率', 0)),
                                debt_to_equity=0.0,  # 需要计算
                                gross_margin=0.0,  # 需要计算
                                last_updated=datetime.now(),
                            )
                            financial_data_list.append(financial_data)
                        except Exception as e:
                            self.logger.warning(f"处理财务数据行失败: {e}")
                            continue

            except Exception as e:
                self.logger.warning(f"获取财务数据失败: {e}")

            self._update_stats('success' if financial_data_list else 'error')
            return financial_data_list

        except Exception as e:
            self._update_stats('error')
            if isinstance(e, DataCollectorError):
                raise
            raise APIError(f"获取财务数据失败: {str(e)}")

    def _format_date_for_akshare(self, date_str: str) -> str:
        """将YYYYMMDD格式转换为YYYY-MM-DD格式"""
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return date_str

    def _get_exchange_from_symbol(self, symbol: str) -> str:
        """根据股票代码判断交易所"""
        if len(symbol) == 6 and symbol.isdigit():
            code_num = int(symbol)
            if code_num >= 600000 and code_num <= 688999:
                return 'SSE'  # 上海证券交易所
            elif code_num >= 000000 and code_num <= 399999:
                return 'SZSE'  # 深圳证券交易所
            elif code_num >= 830000 and code_num <= 899999:
                return 'BSE'  # 北京证券交易所
        return 'UNKNOWN'

    def _parse_market_cap(self, market_cap_str: str) -> Optional[float]:
        """解析市值字符串"""
        if not market_cap_str or market_cap_str == '-':
            return None
        try:
            # 移除单位和格式化
            value_str = market_cap_str.replace('亿', '').replace('万', '').replace(',', '')
            value = float(value_str)
            if '亿' in market_cap_str:
                value *= 100000000
            elif '万' in market_cap_str:
                value *= 10000
            return value
        except:
            return None

    def _parse_shares(self, shares_str: str) -> Optional[int]:
        """解析股本字符串"""
        if not shares_str or shares_str == '-':
            return None
        try:
            value_str = shares_str.replace('亿', '').replace('万', '').replace(',', '')
            value = float(value_str)
            if '亿' in shares_str:
                value *= 100000000
            elif '万' in shares_str:
                value *= 10000
            return int(value)
        except:
            return None

    def _update_stats(self, result_type: str):
        """更新统计信息"""
        if result_type == 'success':
            self.stats['requests_success'] += 1
        elif result_type == 'error':
            self.stats['requests_failed'] += 1

    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        if pd.isna(value) or value is None:
            return 0.0
        try:
            if isinstance(value, str):
                value = value.replace('%', '').replace(',', '')
            return float(value)
        except:
            return 0.0
