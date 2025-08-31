"""
yfinance数据收集器

提供yfinance数据源的统一接口，支持：
- 全球股票数据
- ETF数据
- 指数数据
- 期权数据
- 外汇数据
"""

import yfinance as yf
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


class YFinanceCollector(BaseCollector):
    """yfinance数据收集器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化yfinance收集器

        Args:
            config: 配置字典，可选
        """
        super().__init__(config)
        self.source = "yfinance"
        # 从配置中获取速率限制延迟，处理不同的配置类型
        if hasattr(self.config, 'get'):
            self.rate_limit_delay = self.config.get("rate_limit_delay", 0.5)
        elif hasattr(self.config, 'rate_limit_delay'):
            self.rate_limit_delay = getattr(self.config, 'rate_limit_delay', 0.5)
        else:
            self.rate_limit_delay = 0.5  # 默认值

    def _rate_limit(self):
        """执行速率限制"""
        if hasattr(self, "_last_request_time"):
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

        # 处理中国A股代码，添加后缀
        if len(symbol) == 6 and symbol.isdigit():
            code_num = int(symbol)
            if code_num >= 600000 and code_num <= 688999:
                return f"{symbol}.SS"  # 上海股票
            elif code_num >= 000000 and code_num <= 399999:
                return f"{symbol}.SZ"  # 深圳股票
            elif code_num >= 830000 and code_num <= 899999:
                return f"{symbol}.BJ"  # 北交所

        # 处理港股代码
        if symbol.endswith(".HK") or (len(symbol) <= 5 and symbol.isdigit() and not symbol.isalpha()):
            if not symbol.endswith(".HK"):
                # 补齐港股代码到4位
                symbol = symbol.zfill(4)
                return f"{symbol}.HK"
            return symbol

        # 处理美股代码（通常是字母）
        if symbol.isalpha() and len(symbol) <= 5:
            return symbol

        # 处理其他市场后缀
        market_suffixes = [".SS", ".SZ", ".HK", ".TO", ".L", ".F", ".DE", ".PA", ".T"]
        for suffix in market_suffixes:
            if symbol.endswith(suffix):
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

            # 创建yfinance Ticker对象
            ticker = yf.Ticker(normalized_symbol)

            # 获取股票信息
            info = ticker.info

            if not info or "symbol" not in info:
                raise SymbolNotFoundError(f"股票代码 {symbol} 不存在")

            # 提取基本信息
            return StockInfo(
                symbol=normalized_symbol,
                name=info.get("longName", info.get("shortName", "")),
                exchange=info.get("exchange", ""),
                currency=info.get("currency", "USD"),
                sector=info.get("sector", ""),
                market_cap=info.get("marketCap"),
                shares_outstanding=info.get("sharesOutstanding"),
                last_updated=datetime.now(),
            )

        except Exception as e:
            self._update_stats("error")
            if isinstance(e, (SymbolNotFoundError, DataCollectorError)):
                raise
            raise APIError(f"yfinance API调用失败: {str(e)}")

    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
        adjust: str = "close",
    ) -> List[HistoricalData]:
        """
        获取历史数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD 或 YYYYMMDD)
            end_date: 结束日期 (YYYY-MM-DD 或 YYYYMMDD)
            period: 数据周期 ('daily', 'weekly', 'monthly')
            adjust: 复权类型 ('close'-收盘价复权, 'all'-全部复权, 'none'-不复权)

        Returns:
            List[HistoricalData]: 历史数据列表
        """
        try:
            self._rate_limit()
            normalized_symbol = self._normalize_symbol(symbol)

            # 转换日期格式
            start_date_formatted = self._format_date_for_yfinance(start_date)
            end_date_formatted = self._format_date_for_yfinance(end_date)

            # 创建yfinance Ticker对象
            ticker = yf.Ticker(normalized_symbol)

            # 设置间隔
            interval_map = {"daily": "1d", "weekly": "1wk", "monthly": "1mo"}
            interval = interval_map.get(period, "1d")

            # 获取历史数据
            hist_data = ticker.history(
                start=start_date_formatted,
                end=end_date_formatted,
                interval=interval,
                auto_adjust=(adjust == "all"),
                back_adjust=(adjust == "close"),
            )

            if hist_data.empty:
                return []

            # 转换数据格式
            historical_data = []
            for date, row in hist_data.iterrows():
                # 计算涨跌幅
                change = 0.0
                change_pct = 0.0
                if len(historical_data) > 0:
                    prev_close = historical_data[-1].close
                    change = float(row["Close"]) - prev_close
                    change_pct = (change / prev_close) * 100 if prev_close != 0 else 0.0

                data = HistoricalData(
                    symbol=normalized_symbol,
                    date=date.date(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
                    amount=0.0,  # yfinance不直接提供成交额
                    change=change,
                    change_pct=change_pct,
                    turnover=0.0,  # yfinance不直接提供换手率
                    last_updated=datetime.now(),
                )
                historical_data.append(data)

            self._update_stats("success")
            return historical_data

        except Exception as e:
            self._update_stats("error")
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

            # 创建yfinance Ticker对象
            ticker = yf.Ticker(normalized_symbol)

            # 获取最新的历史数据（当日数据）
            hist_data = ticker.history(period="2d", interval="1d")
            if hist_data.empty or len(hist_data) < 1:
                raise DataNotAvailableError(f"无法获取股票 {symbol} 的实时数据")

            latest_row = hist_data.iloc[-1]
            prev_row = hist_data.iloc[-2] if len(hist_data) > 1 else latest_row

            # 获取快速信息
            fast_info = ticker.fast_info
            current_price = fast_info.get("lastPrice", float(latest_row["Close"]))

            # 计算涨跌
            previous_close = float(prev_row["Close"])
            change = current_price - previous_close
            change_pct = (change / previous_close) * 100 if previous_close != 0 else 0.0

            realtime_data = RealtimeData(
                symbol=normalized_symbol,
                current_price=current_price,
                open_price=float(latest_row["Open"]),
                high_price=float(latest_row["High"]),
                low_price=float(latest_row["Low"]),
                previous_close=previous_close,
                volume=int(latest_row["Volume"]) if pd.notna(latest_row["Volume"]) else 0,
                amount=0.0,  # yfinance不直接提供成交额
                change=change,
                change_pct=change_pct,
                turnover=0.0,  # yfinance不直接提供换手率
                timestamp=datetime.now(),
                last_updated=datetime.now(),
            )

            self._update_stats("success")
            return realtime_data

        except Exception as e:
            self._update_stats("error")
            if isinstance(e, DataCollectorError):
                raise
            raise APIError(f"获取实时数据失败: {str(e)}")

    def get_financial_data(self, symbol: str, report_type: str = "annual") -> List[FinancialData]:
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

            # 创建yfinance Ticker对象
            ticker = yf.Ticker(normalized_symbol)

            financial_data_list = []

            # 获取财务数据
            if report_type == "annual":
                income_stmt = ticker.financials
                balance_sheet = ticker.balance_sheet
            else:  # quarterly
                income_stmt = ticker.quarterly_financials
                balance_sheet = ticker.quarterly_balance_sheet

            if income_stmt.empty and balance_sheet.empty:
                return []

            # 获取所有可用的报告日期
            dates = set()
            if not income_stmt.empty:
                dates.update(income_stmt.columns)
            if not balance_sheet.empty:
                dates.update(balance_sheet.columns)

            # 处理每个报告期的数据
            for date in sorted(dates, reverse=True):
                try:
                    # 从利润表获取数据
                    revenue = 0.0
                    net_income = 0.0
                    if not income_stmt.empty and date in income_stmt.columns:
                        revenue = self._safe_float_yf(income_stmt.loc["Total Revenue", date])
                        net_income = self._safe_float_yf(income_stmt.loc["Net Income", date])

                    # 从资产负债表获取数据
                    total_assets = 0.0
                    total_equity = 0.0
                    if not balance_sheet.empty and date in balance_sheet.columns:
                        total_assets = self._safe_float_yf(balance_sheet.loc["Total Assets", date])
                        total_equity = self._safe_float_yf(balance_sheet.loc["Stockholders Equity", date])

                    # 计算财务比率
                    roe = 0.0
                    debt_to_equity = 0.0
                    gross_margin = 0.0

                    if total_equity != 0:
                        roe = (net_income / total_equity) * 100
                        total_debt = total_assets - total_equity
                        debt_to_equity = total_debt / total_equity

                    if revenue != 0 and not income_stmt.empty and date in income_stmt.columns:
                        try:
                            gross_profit = self._safe_float_yf(income_stmt.loc["Gross Profit", date])
                            gross_margin = (gross_profit / revenue) * 100
                        except KeyError:
                            pass

                    # 获取EPS（从info或计算）
                    eps = 0.0
                    try:
                        info = ticker.info
                        if report_type == "annual":
                            eps = info.get("trailingEps", 0.0)
                        else:
                            eps = info.get("forwardEps", 0.0)
                    except:
                        pass

                    financial_data = FinancialData(
                        symbol=normalized_symbol,
                        report_date=date.date(),
                        report_type=report_type,
                        revenue=revenue,
                        net_income=net_income,
                        total_assets=total_assets,
                        total_equity=total_equity,
                        eps=eps,
                        roe=roe,
                        debt_to_equity=debt_to_equity,
                        gross_margin=gross_margin,
                        last_updated=datetime.now(),
                    )
                    financial_data_list.append(financial_data)

                except Exception as e:
                    self.logger.warning(f"处理财务数据失败 (日期: {date}): {e}")
                    continue

            self._update_stats("success" if financial_data_list else "error")
            return financial_data_list

        except Exception as e:
            self._update_stats("error")
            if isinstance(e, DataCollectorError):
                raise
            raise APIError(f"获取财务数据失败: {str(e)}")

    def _format_date_for_yfinance(self, date_str: str) -> str:
        """将YYYYMMDD格式转换为YYYY-MM-DD格式"""
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return date_str

    def _safe_float_yf(self, value) -> float:
        """安全转换yfinance数据为浮点数"""
        if pd.isna(value) or value is None:
            return 0.0
        try:
            return float(value)
        except:
            return 0.0

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        获取汇率数据

        Args:
            from_currency: 源货币代码
            to_currency: 目标货币代码

        Returns:
            float: 汇率，如果获取失败返回None
        """
        try:
            self._rate_limit()
            symbol = f"{from_currency}{to_currency}=X"
            ticker = yf.Ticker(symbol)

            # 获取最新价格
            hist_data = ticker.history(period="1d")
            if hist_data.empty:
                return None

            return float(hist_data["Close"].iloc[-1])

        except Exception as e:
            self.logger.warning(f"获取汇率失败 {from_currency}/{to_currency}: {e}")
            return None

    def get_index_data(self, index_symbol: str) -> Optional[RealtimeData]:
        """
        获取指数数据

        Args:
            index_symbol: 指数代码

        Returns:
            RealtimeData: 指数实时数据
        """
        try:
            # 常见指数代码映射
            index_map = {
                "SPX": "^GSPC",  # S&P 500
                "DJI": "^DJI",  # Dow Jones
                "NASDAQ": "^IXIC",  # NASDAQ
                "HSI": "^HSI",  # 恒生指数
                "NIKKEI": "^N225",  # 日经225
                "FTSE": "^FTSE",  # 富时100
            }

            symbol = index_map.get(index_symbol.upper(), index_symbol)
            return self.get_realtime_data(symbol)

        except Exception as e:
            self.logger.warning(f"获取指数数据失败 {index_symbol}: {e}")
            return None
