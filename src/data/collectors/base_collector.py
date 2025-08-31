"""
基础数据收集器抽象类

定义所有数据收集器的统一接口和通用功能。
"""

import time
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date, timedelta
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .data_types import (
    StockInfo,
    HistoricalData,
    RealtimeData,
    FinancialData,
    DataCollectorConfig,
    StockSymbol,
    DateRange,
)
from .exceptions import (
    DataCollectorError,
    APIError,
    RateLimitError,
    NetworkError,
    ValidationError,
    RetryExhaustedError,
    ConfigurationError,
)
from ...utils.config import get_config
from ...utils.logger import get_database_logger


class BaseCollector(ABC):
    """数据收集器基础抽象类"""

    def __init__(self, name: str, config: Optional[DataCollectorConfig] = None):
        """
        初始化基础收集器

        Args:
            name: 收集器名称
            config: 收集器配置，如果为None则从配置文件加载
        """
        self.name = name
        self.logger = get_database_logger()
        self.app_config = get_config()

        # 加载配置
        if config is None:
            config = self._load_config_from_file()
        self.config = config

        # 初始化HTTP会话
        self.session = self._create_session()

        # 统计信息
        self.stats = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'last_request_time': None,
            'rate_limit_hits': 0,
        }

    def _load_config_from_file(self) -> DataCollectorConfig:
        """从配置文件加载收集器配置"""
        try:
            # 获取数据源配置
            if hasattr(self.app_config, 'config') and self.app_config.config:
                data_sources = self.app_config.config.get('data_sources', {})
            else:
                # 如果配置对象不存在，直接从文件读取
                import yaml
                import os

                config_path = os.path.join(os.getcwd(), 'config', 'config.yaml')
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                    data_sources = config_data.get('data_sources', {})
                else:
                    data_sources = {}

            source_config = data_sources.get(self.name.lower(), {})

            return DataCollectorConfig(
                timeout=source_config.get('timeout', 30),
                retry_count=source_config.get('retry_count', 3),
                token=source_config.get('token'),
            )
        except Exception as e:
            self.logger.warning(f"加载配置失败，使用默认配置: {e}")
            return DataCollectorConfig()

    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=self.config.retry_count,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 设置默认headers
        if self.config.custom_headers:
            session.headers.update(self.config.custom_headers)

        # 设置代理
        if self.config.proxy:
            session.proxies.update(self.config.proxy)

        return session

    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        发起HTTP请求

        Args:
            method: HTTP方法
            url: 请求URL
            params: URL参数
            data: POST数据
            headers: 额外的请求头
            **kwargs: 其他参数

        Returns:
            响应对象

        Raises:
            APIError: API调用错误
            RateLimitError: 频率限制错误
            NetworkError: 网络错误
        """
        self.stats['requests_total'] += 1
        self.stats['last_request_time'] = datetime.now()

        try:
            # 频率限制检查
            self._check_rate_limit()

            # 合并headers
            request_headers = {}
            if headers:
                request_headers.update(headers)

            self.logger.debug(f"发起请求: {method.upper()} {url}")

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=request_headers,
                timeout=self.config.timeout,
                **kwargs,
            )

            # 检查响应状态
            if response.status_code == 429:
                self.stats['rate_limit_hits'] += 1
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError(
                    f"API频率限制: {response.status_code}",
                    retry_after=retry_after,
                    rate_limit_type='http_429',
                )

            response.raise_for_status()
            self.stats['requests_success'] += 1

            return response

        except requests.exceptions.Timeout as e:
            self.stats['requests_failed'] += 1
            raise NetworkError(f"请求超时: {e}", timeout=self.config.timeout, url=url)

        except requests.exceptions.ConnectionError as e:
            self.stats['requests_failed'] += 1
            raise NetworkError(f"连接错误: {e}", url=url)

        except requests.exceptions.HTTPError as e:
            self.stats['requests_failed'] += 1
            raise APIError(
                f"HTTP错误: {e}",
                status_code=response.status_code,
                response_text=response.text[:500],
                api_name=self.name,
            )

        except Exception as e:
            self.stats['requests_failed'] += 1
            if isinstance(e, (RateLimitError, NetworkError, APIError)):
                raise
            raise DataCollectorError(f"请求失败: {e}")

    def _check_rate_limit(self):
        """检查频率限制"""
        # 基础实现：简单的延迟
        if self.config.rate_limit_delay > 0:
            time.sleep(self.config.rate_limit_delay)

    def _retry_on_failure(self, func, *args, max_retries: Optional[int] = None, **kwargs):
        """
        失败重试装饰器

        Args:
            func: 要重试的函数
            max_retries: 最大重试次数
            *args, **kwargs: 函数参数

        Returns:
            函数执行结果

        Raises:
            RetryExhaustedError: 重试次数耗尽
        """
        if max_retries is None:
            max_retries = self.config.retry_count

        last_error = None
        delay = self.config.retry_delay

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (NetworkError, APIError) as e:
                last_error = e
                if attempt < max_retries:
                    self.logger.warning(f"第{attempt + 1}次尝试失败，{delay}秒后重试: {e}")
                    time.sleep(delay)
                    delay = min(delay * 2, self.config.max_retry_delay)  # 指数退避
                else:
                    break
            except Exception as e:
                # 对于非网络/API错误，不进行重试
                raise e

        raise RetryExhaustedError(
            f"重试{max_retries}次后仍然失败", max_retries=max_retries, last_error=last_error
        )

    def _validate_symbol(self, symbol: str) -> str:
        """
        验证股票代码格式

        Args:
            symbol: 股票代码

        Returns:
            标准化的股票代码

        Raises:
            ValidationError: 格式验证错误
        """
        if not symbol or not isinstance(symbol, str):
            raise ValidationError(
                "股票代码不能为空且必须是字符串", parameter='symbol', expected_type='str', actual_value=symbol
            )

        symbol = symbol.strip().upper()
        if not symbol:
            raise ValidationError("股票代码不能为空字符串", parameter='symbol', actual_value=symbol)

        return symbol

    def _validate_date_range(
        self, start_date: Union[str, date], end_date: Union[str, date]
    ) -> tuple[date, date]:
        """
        验证日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            标准化的日期范围元组

        Raises:
            ValidationError: 日期验证错误
        """

        def parse_date(date_input: Union[str, date]) -> date:
            if isinstance(date_input, date):
                return date_input
            elif isinstance(date_input, str):
                try:
                    return datetime.strptime(date_input, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        return datetime.strptime(date_input, '%Y%m%d').date()
                    except ValueError:
                        raise ValidationError(
                            f"日期格式不正确: {date_input}，期望格式: YYYY-MM-DD 或 YYYYMMDD",
                            parameter='date',
                            expected_type='YYYY-MM-DD',
                            actual_value=date_input,
                        )
            else:
                raise ValidationError(
                    f"日期类型不正确: {type(date_input)}",
                    parameter='date',
                    expected_type='str or date',
                    actual_value=date_input,
                )

        start = parse_date(start_date)
        end = parse_date(end_date)

        if start > end:
            raise ValidationError(
                f"开始日期不能晚于结束日期: {start} > {end}",
                parameter='date_range',
                actual_value=(start, end),
            )

        return start, end

    def _standardize_dataframe(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        标准化DataFrame格式

        Args:
            df: 原始DataFrame
            data_type: 数据类型

        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df

        # 统一列名格式（小写，下划线分隔）
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # 处理日期列
        date_columns = ['date', 'trade_date', 'ann_date', 'report_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

        # 处理时间戳列
        timestamp_columns = ['timestamp', 'datetime', 'update_time']
        for col in timestamp_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # 处理数值列
        numeric_columns = [
            'open',
            'high',
            'low',
            'close',
            'volume',
            'amount',
            'price',
            'change',
            'pct_change',
            'turnover_rate',
            'pe_ratio',
            'pb_ratio',
            'market_cap',
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'last_request_time': None,
            'rate_limit_hits': 0,
        }

    # 抽象方法：子类必须实现
    @abstractmethod
    def get_stock_info(self, symbol: StockSymbol) -> StockInfo:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            股票基本信息

        Raises:
            SymbolNotFoundError: 股票代码未找到
            DataCollectorError: 其他错误
        """
        pass

    @abstractmethod
    def get_historical_data(
        self, symbol: StockSymbol, start_date: Union[str, date], end_date: Union[str, date], **kwargs
    ) -> List[HistoricalData]:
        """
        获取历史行情数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数

        Returns:
            历史行情数据列表

        Raises:
            DataNotAvailableError: 数据不可用
            DataCollectorError: 其他错误
        """
        pass

    @abstractmethod
    def get_realtime_data(self, symbols: Union[StockSymbol, List[StockSymbol]]) -> List[RealtimeData]:
        """
        获取实时行情数据

        Args:
            symbols: 股票代码或股票代码列表

        Returns:
            实时行情数据列表

        Raises:
            DataNotAvailableError: 数据不可用
            DataCollectorError: 其他错误
        """
        pass

    @abstractmethod
    def get_financial_data(
        self, symbol: StockSymbol, report_type: str = 'annual', **kwargs
    ) -> List[FinancialData]:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            report_type: 报告类型 ('annual', 'quarter')
            **kwargs: 其他参数

        Returns:
            财务数据列表

        Raises:
            DataNotAvailableError: 数据不可用
            DataCollectorError: 其他错误
        """
        pass

    # 可选的批量方法
    def get_historical_data_batch(
        self, symbols: List[StockSymbol], start_date: Union[str, date], end_date: Union[str, date], **kwargs
    ) -> Dict[str, List[HistoricalData]]:
        """
        批量获取历史行情数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数

        Returns:
            股票代码到历史数据的映射

        Raises:
            DataCollectorError: 错误
        """
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = self.get_historical_data(symbol, start_date, end_date, **kwargs)
            except Exception as e:
                self.logger.error(f"获取{symbol}历史数据失败: {e}")
                result[symbol] = []
        return result

    def close(self):
        """关闭收集器，清理资源"""
        if hasattr(self, 'session'):
            self.session.close()
        self.logger.info(f"{self.name} 收集器已关闭")
