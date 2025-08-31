"""
Tushare数据收集器

提供Tushare数据源的数据收集功能，包括股票基本信息、历史行情、实时数据和财务数据。

使用前需要：
1. 注册Tushare账号获取token
2. 在配置文件中设置TUSHARE_TOKEN环境变量
"""

import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date, timedelta
import pandas as pd

from .base_collector import BaseCollector
from .data_types import (
    StockInfo,
    HistoricalData,
    RealtimeData,
    FinancialData,
    DataCollectorConfig,
    StockSymbol,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    SymbolNotFoundError,
    DataNotAvailableError,
    DataQualityError,
    ValidationError,
    DataCollectorError,
)

try:
    import tushare as ts
except ImportError:
    ts = None


class TushareCollector(BaseCollector):
    """Tushare数据收集器"""

    def __init__(self, config: Optional[DataCollectorConfig] = None):
        """
        初始化Tushare收集器

        Args:
            config: 收集器配置

        Raises:
            ImportError: tushare库未安装
            AuthenticationError: token配置错误
        """
        super().__init__("tushare", config)

        if ts is None:
            raise ImportError("请安装tushare库: pip install tushare")

        # 设置token
        if not self.config.token:
            raise AuthenticationError(
                "Tushare token未配置，请在配置文件中设置TUSHARE_TOKEN环境变量", auth_type='tushare_token'
            )

        try:
            ts.set_token(self.config.token)
            self.pro = ts.pro_api()
            self.logger.info("Tushare API初始化成功")
        except Exception as e:
            raise AuthenticationError(f"Tushare API初始化失败: {e}", auth_type='tushare_token')

        # Tushare特殊配置
        self.daily_request_limit = 10000  # 每日请求限制
        self.request_interval = 0.1  # 请求间隔(秒)
        self.last_request_time = None

    def _check_rate_limit(self):
        """检查Tushare特殊的频率限制"""
        current_time = time.time()
        if self.last_request_time:
            elapsed = current_time - self.last_request_time
            if elapsed < self.request_interval:
                sleep_time = self.request_interval - elapsed
                time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _call_tushare_api(self, api_name: str, **kwargs) -> pd.DataFrame:
        """
        调用Tushare API

        Args:
            api_name: API名称
            **kwargs: API参数

        Returns:
            返回的DataFrame

        Raises:
            APIError: API调用错误
            RateLimitError: 频率限制
        """
        self._check_rate_limit()

        try:
            self.logger.debug(f"调用Tushare API: {api_name}, 参数: {kwargs}")

            api_func = getattr(self.pro, api_name)
            df = api_func(**kwargs)

            if df is None or df.empty:
                self.logger.warning(f"Tushare API {api_name} 返回空数据")
                return pd.DataFrame()

            self.stats['requests_success'] += 1
            return df

        except Exception as e:
            self.stats['requests_failed'] += 1
            error_msg = str(e)

            # 检查是否是积分不足错误
            if "积分不足" in error_msg or "权限不足" in error_msg:
                raise RateLimitError(
                    f"Tushare积分不足或权限不足: {error_msg}", rate_limit_type='tushare_points'
                )

            # 检查是否是频率限制
            if "请求过于频繁" in error_msg or "rate limit" in error_msg.lower():
                raise RateLimitError(
                    f"Tushare请求频率限制: {error_msg}", retry_after=60, rate_limit_type='tushare_frequency'
                )

            raise APIError(f"Tushare API调用失败: {error_msg}", api_name=api_name)

    def _normalize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码为Tushare格式

        Args:
            symbol: 原始股票代码

        Returns:
            Tushare格式的股票代码 (如: 000001.SZ)
        """
        symbol = self._validate_symbol(symbol)

        # 如果已经是Tushare格式，直接返回
        if '.' in symbol and symbol.count('.') == 1:
            code, exchange = symbol.split('.')
            if exchange.upper() in ['SZ', 'SH', 'BJ'] and len(code) == 6:
                return f"{code}.{exchange.upper()}"

        # 处理6位数字代码
        if symbol.isdigit() and len(symbol) == 6:
            # 根据代码判断交易所
            if symbol.startswith(('000', '001', '002', '003', '300')):
                return f"{symbol}.SZ"
            elif symbol.startswith(('600', '601', '603', '605', '688')):
                return f"{symbol}.SH"
            elif symbol.startswith(('430', '831', '832', '833', '834', '835', '836', '837', '838', '839')):
                return f"{symbol}.BJ"

        # 处理其他格式
        if symbol.endswith(('.SZ', '.sz')):
            return symbol.replace('.sz', '.SZ')
        elif symbol.endswith(('.SH', '.sh')):
            return symbol.replace('.sh', '.SH')
        elif symbol.endswith(('.BJ', '.bj')):
            return symbol.replace('.bj', '.BJ')

        raise ValidationError(
            f"无法识别的股票代码格式: {symbol}",
            parameter='symbol',
            expected_type='6位数字或包含交易所后缀',
            actual_value=symbol,
        )

    def get_stock_info(self, symbol: StockSymbol) -> StockInfo:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            股票基本信息

        Raises:
            SymbolNotFoundError: 股票代码未找到
        """
        ts_symbol = self._normalize_symbol(symbol)

        try:
            # 获取股票基本信息
            df = self._call_tushare_api('stock_basic', ts_code=ts_symbol)

            if df.empty:
                raise SymbolNotFoundError(f"未找到股票: {symbol}", symbol=symbol, data_source='tushare')

            row = df.iloc[0]

            # 解析交易所
            exchange_map = {'SZ': '深圳证券交易所', 'SH': '上海证券交易所', 'BJ': '北京证券交易所'}
            exchange = exchange_map.get(ts_symbol.split('.')[1], '未知')

            # 解析市场类型
            code = ts_symbol.split('.')[0]
            if code.startswith('000'):
                market = '深市主板'
            elif code.startswith('001'):
                market = '深市主板'
            elif code.startswith('002'):
                market = '深市中小板'
            elif code.startswith('300'):
                market = '创业板'
            elif code.startswith(('600', '601', '603', '605')):
                market = '沪市主板'
            elif code.startswith('688'):
                market = '科创板'
            elif code.startswith(('430', '831', '832', '833', '834', '835', '836', '837', '838', '839')):
                market = '新三板'
            else:
                market = '其他'

            # 转换上市日期
            list_date = None
            if pd.notna(row.get('list_date')):
                try:
                    list_date = pd.to_datetime(str(row['list_date'])).date()
                except:
                    pass

            # 转换退市日期
            delist_date = None
            if pd.notna(row.get('delist_date')):
                try:
                    delist_date = pd.to_datetime(str(row['delist_date'])).date()
                except:
                    pass

            return StockInfo(
                symbol=ts_symbol,
                name=row.get('name', ''),
                exchange=exchange,
                market=market,
                industry=row.get('industry', None),
                sector=row.get('area', None),
                list_date=list_date,
                delist_date=delist_date,
                is_active=row.get('list_status', 'L') == 'L',
                currency='CNY',
                metadata={
                    'tushare_code': ts_symbol,
                    'fullname': row.get('fullname', ''),
                    'enname': row.get('enname', ''),
                    'market': row.get('market', ''),
                    'list_status': row.get('list_status', ''),
                    'is_hs': row.get('is_hs', ''),
                },
            )

        except SymbolNotFoundError:
            raise
        except Exception as e:
            raise DataCollectorError(f"获取股票信息失败: {e}")

    def get_historical_data(
        self,
        symbol: StockSymbol,
        start_date: Union[str, date],
        end_date: Union[str, date],
        adj: str = 'qfq',
        **kwargs,
    ) -> List[HistoricalData]:
        """
        获取历史行情数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adj: 复权类型 ('qfq'-前复权, 'hfq'-后复权, None-不复权)
            **kwargs: 其他参数

        Returns:
            历史行情数据列表
        """
        ts_symbol = self._normalize_symbol(symbol)
        start, end = self._validate_date_range(start_date, end_date)

        try:
            # 转换日期格式为YYYYMMDD
            start_str = start.strftime('%Y%m%d')
            end_str = end.strftime('%Y%m%d')

            # 获取历史行情数据
            if adj:
                # 获取复权数据
                df = self._call_tushare_api(
                    'pro_bar', ts_code=ts_symbol, start_date=start_str, end_date=end_str, adj=adj, freq='D'
                )
            else:
                # 获取未复权数据
                df = self._call_tushare_api(
                    'daily', ts_code=ts_symbol, start_date=start_str, end_date=end_str
                )

            if df.empty:
                raise DataNotAvailableError(
                    f"未找到股票 {symbol} 在 {start} 到 {end} 期间的历史数据",
                    symbol=symbol,
                    date_range=(start, end),
                    data_type='historical',
                )

            # 标准化DataFrame
            df = self._standardize_dataframe(df, 'historical')

            # 转换为HistoricalData对象列表
            historical_data = []
            for _, row in df.iterrows():
                # 处理日期
                trade_date = row.get('trade_date')
                if pd.isna(trade_date):
                    continue

                if isinstance(trade_date, str):
                    trade_date = datetime.strptime(trade_date, '%Y%m%d').date()
                elif isinstance(trade_date, pd.Timestamp):
                    trade_date = trade_date.date()

                historical_data.append(
                    HistoricalData(
                        symbol=ts_symbol,
                        date=trade_date,
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row.get('close'),
                        volume=row.get('vol'),  # Tushare中成交量字段为vol
                        amount=row.get('amount'),
                        pre_close=row.get('pre_close'),
                        change=row.get('change'),
                        pct_change=row.get('pct_chg'),  # Tushare中涨跌幅字段为pct_chg
                        metadata={
                            'adj_type': adj,
                            'source': 'tushare',
                        },
                    )
                )

            # 按日期排序
            historical_data.sort(key=lambda x: x.date)

            self.logger.info(f"获取到 {len(historical_data)} 条历史数据: {symbol}")
            return historical_data

        except DataNotAvailableError:
            raise
        except Exception as e:
            raise DataCollectorError(f"获取历史数据失败: {e}")

    def get_realtime_data(self, symbols: Union[StockSymbol, List[StockSymbol]]) -> List[RealtimeData]:
        """
        获取实时行情数据

        Args:
            symbols: 股票代码或股票代码列表

        Returns:
            实时行情数据列表

        Note:
            Tushare的实时数据需要特殊权限，这里提供模拟实现
        """
        if isinstance(symbols, str):
            symbols = [symbols]

        ts_symbols = [self._normalize_symbol(symbol) for symbol in symbols]

        try:
            # 由于Tushare实时数据需要特殊权限，这里获取最新的日行情作为替代
            realtime_data = []

            for ts_symbol in ts_symbols:
                try:
                    # 获取最近5个交易日的数据
                    df = self._call_tushare_api('daily', ts_code=ts_symbol, limit=5)

                    if df.empty:
                        continue

                    # 取最新的一条数据
                    latest = df.iloc[0]

                    # 获取股票名称
                    stock_info = self._call_tushare_api('stock_basic', ts_code=ts_symbol)
                    name = stock_info.iloc[0]['name'] if not stock_info.empty else ts_symbol

                    realtime_data.append(
                        RealtimeData(
                            symbol=ts_symbol,
                            name=name,
                            timestamp=datetime.now(),  # 由于是日行情，使用当前时间作为时间戳
                            current_price=latest.get('close'),
                            open=latest.get('open'),
                            high=latest.get('high'),
                            low=latest.get('low'),
                            pre_close=latest.get('pre_close'),
                            volume=latest.get('vol'),
                            amount=latest.get('amount'),
                            change=latest.get('change'),
                            pct_change=latest.get('pct_chg'),
                            status='trading',
                            metadata={
                                'source': 'tushare',
                                'data_type': 'daily_latest',
                                'trade_date': latest.get('trade_date'),
                            },
                        )
                    )

                except Exception as e:
                    self.logger.error(f"获取 {ts_symbol} 实时数据失败: {e}")
                    continue

            return realtime_data

        except Exception as e:
            raise DataCollectorError(f"获取实时数据失败: {e}")

    def get_financial_data(
        self, symbol: StockSymbol, report_type: str = 'annual', **kwargs
    ) -> List[FinancialData]:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            report_type: 报告类型 ('annual'-年报, 'quarter'-季报)
            **kwargs: 其他参数

        Returns:
            财务数据列表
        """
        ts_symbol = self._normalize_symbol(symbol)

        try:
            financial_data = []

            # 获取资产负债表数据
            balancesheet_df = self._call_tushare_api(
                'balancesheet',
                ts_code=ts_symbol,
                period=kwargs.get('period'),
                report_type=1 if report_type == 'annual' else None,
            )

            # 获取利润表数据
            income_df = self._call_tushare_api(
                'income',
                ts_code=ts_symbol,
                period=kwargs.get('period'),
                report_type=1 if report_type == 'annual' else None,
            )

            # 获取现金流量表数据
            cashflow_df = self._call_tushare_api(
                'cashflow',
                ts_code=ts_symbol,
                period=kwargs.get('period'),
                report_type=1 if report_type == 'annual' else None,
            )

            # 合并数据
            all_periods = set()
            if not balancesheet_df.empty:
                all_periods.update(balancesheet_df['end_date'].tolist())
            if not income_df.empty:
                all_periods.update(income_df['end_date'].tolist())
            if not cashflow_df.empty:
                all_periods.update(cashflow_df['end_date'].tolist())

            for period in sorted(all_periods, reverse=True):
                try:
                    # 解析报告期
                    report_date = datetime.strptime(period, '%Y%m%d').date()

                    # 获取对应期间的数据
                    balance_row = balancesheet_df[balancesheet_df['end_date'] == period]
                    income_row = income_df[income_df['end_date'] == period]
                    cashflow_row = cashflow_df[cashflow_df['end_date'] == period]

                    # 解析公告日期
                    ann_date = None
                    for df in [balance_row, income_row, cashflow_row]:
                        if not df.empty and pd.notna(df.iloc[0].get('ann_date')):
                            try:
                                ann_date = datetime.strptime(str(df.iloc[0]['ann_date']), '%Y%m%d').date()
                                break
                            except:
                                pass

                    financial_data.append(
                        FinancialData(
                            symbol=ts_symbol,
                            report_date=report_date,
                            ann_date=ann_date,
                            # 资产负债表数据
                            total_assets=(
                                balance_row.iloc[0].get('total_assets') if not balance_row.empty else None
                            ),
                            total_liabilities=(
                                balance_row.iloc[0].get('total_liab') if not balance_row.empty else None
                            ),
                            total_equity=(
                                balance_row.iloc[0].get('total_equity') if not balance_row.empty else None
                            ),
                            current_assets=(
                                balance_row.iloc[0].get('total_cur_assets') if not balance_row.empty else None
                            ),
                            current_liabilities=(
                                balance_row.iloc[0].get('total_cur_liab') if not balance_row.empty else None
                            ),
                            # 利润表数据
                            total_revenue=(
                                income_row.iloc[0].get('total_revenue') if not income_row.empty else None
                            ),
                            net_profit=income_row.iloc[0].get('n_income') if not income_row.empty else None,
                            operating_profit=(
                                income_row.iloc[0].get('operate_profit') if not income_row.empty else None
                            ),
                            # 现金流量表数据
                            net_cash_flow_operating=(
                                cashflow_row.iloc[0].get('n_cashflow_act') if not cashflow_row.empty else None
                            ),
                            net_cash_flow_investing=(
                                cashflow_row.iloc[0].get('n_cashflow_inv_act')
                                if not cashflow_row.empty
                                else None
                            ),
                            net_cash_flow_financing=(
                                cashflow_row.iloc[0].get('n_cashflow_fin_act')
                                if not cashflow_row.empty
                                else None
                            ),
                            metadata={
                                'source': 'tushare',
                                'report_type': report_type,
                                'period': period,
                            },
                        )
                    )

                except Exception as e:
                    self.logger.error(f"解析财务数据失败 {period}: {e}")
                    continue

            self.logger.info(f"获取到 {len(financial_data)} 期财务数据: {symbol}")
            return financial_data

        except Exception as e:
            raise DataCollectorError(f"获取财务数据失败: {e}")

    def get_stock_list(self, exchange: Optional[str] = None) -> List[StockInfo]:
        """
        获取股票列表

        Args:
            exchange: 交易所 ('SSE'-上交所, 'SZSE'-深交所, 'BSE'-北交所)

        Returns:
            股票信息列表
        """
        try:
            params = {}
            if exchange:
                exchange_map = {'SSE': 'SH', 'SZSE': 'SZ', 'BSE': 'BJ'}
                params['exchange'] = exchange_map.get(exchange.upper(), exchange)

            df = self._call_tushare_api('stock_basic', **params)

            stock_list = []
            for _, row in df.iterrows():
                try:
                    stock_info = self.get_stock_info(row['ts_code'])
                    stock_list.append(stock_info)
                except Exception as e:
                    self.logger.error(f"获取股票信息失败 {row['ts_code']}: {e}")
                    continue

            return stock_list

        except Exception as e:
            raise DataCollectorError(f"获取股票列表失败: {e}")
