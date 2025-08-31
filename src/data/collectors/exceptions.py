"""
数据收集模块自定义异常类

定义数据收集过程中可能出现的各种异常。
"""

from typing import Optional, Dict, Any


class DataCollectorError(Exception):
    """数据收集器基础异常类"""

    def __init__(
        self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details,
        }


class APIError(DataCollectorError):
    """API调用错误"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
        api_name: Optional[str] = None,
        **kwargs,
    ):
        details = {'status_code': status_code, 'response_text': response_text, 'api_name': api_name, **kwargs}
        super().__init__(message, error_code='API_ERROR', details=details)
        self.status_code = status_code
        self.response_text = response_text
        self.api_name = api_name


class RateLimitError(DataCollectorError):
    """频率限制错误"""

    def __init__(
        self, message: str, retry_after: Optional[int] = None, rate_limit_type: Optional[str] = None, **kwargs
    ):
        details = {'retry_after': retry_after, 'rate_limit_type': rate_limit_type, **kwargs}
        super().__init__(message, error_code='RATE_LIMIT', details=details)
        self.retry_after = retry_after
        self.rate_limit_type = rate_limit_type


class AuthenticationError(DataCollectorError):
    """认证错误"""

    def __init__(self, message: str, auth_type: Optional[str] = None, **kwargs):
        details = {'auth_type': auth_type, **kwargs}
        super().__init__(message, error_code='AUTH_ERROR', details=details)
        self.auth_type = auth_type


class DataQualityError(DataCollectorError):
    """数据质量错误"""

    def __init__(
        self,
        message: str,
        data_source: Optional[str] = None,
        symbol: Optional[str] = None,
        missing_fields: Optional[list] = None,
        invalid_fields: Optional[list] = None,
        **kwargs,
    ):
        details = {
            'data_source': data_source,
            'symbol': symbol,
            'missing_fields': missing_fields or [],
            'invalid_fields': invalid_fields or [],
            **kwargs,
        }
        super().__init__(message, error_code='DATA_QUALITY', details=details)
        self.data_source = data_source
        self.symbol = symbol
        self.missing_fields = missing_fields or []
        self.invalid_fields = invalid_fields or []


class NetworkError(DataCollectorError):
    """网络连接错误"""

    def __init__(self, message: str, timeout: Optional[float] = None, url: Optional[str] = None, **kwargs):
        details = {'timeout': timeout, 'url': url, **kwargs}
        super().__init__(message, error_code='NETWORK_ERROR', details=details)
        self.timeout = timeout
        self.url = url


class ConfigurationError(DataCollectorError):
    """配置错误"""

    def __init__(
        self, message: str, config_key: Optional[str] = None, config_value: Optional[Any] = None, **kwargs
    ):
        details = {'config_key': config_key, 'config_value': config_value, **kwargs}
        super().__init__(message, error_code='CONFIG_ERROR', details=details)
        self.config_key = config_key
        self.config_value = config_value


class SymbolNotFoundError(DataCollectorError):
    """股票代码未找到错误"""

    def __init__(self, message: str, symbol: str, data_source: Optional[str] = None, **kwargs):
        details = {'symbol': symbol, 'data_source': data_source, **kwargs}
        super().__init__(message, error_code='SYMBOL_NOT_FOUND', details=details)
        self.symbol = symbol
        self.data_source = data_source


class DataNotAvailableError(DataCollectorError):
    """数据不可用错误"""

    def __init__(
        self,
        message: str,
        symbol: Optional[str] = None,
        date_range: Optional[tuple] = None,
        data_type: Optional[str] = None,
        **kwargs,
    ):
        details = {'symbol': symbol, 'date_range': date_range, 'data_type': data_type, **kwargs}
        super().__init__(message, error_code='DATA_NOT_AVAILABLE', details=details)
        self.symbol = symbol
        self.date_range = date_range
        self.data_type = data_type


class ValidationError(DataCollectorError):
    """参数验证错误"""

    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs,
    ):
        details = {
            'parameter': parameter,
            'expected_type': expected_type,
            'actual_value': actual_value,
            **kwargs,
        }
        super().__init__(message, error_code='VALIDATION_ERROR', details=details)
        self.parameter = parameter
        self.expected_type = expected_type
        self.actual_value = actual_value


class RetryExhaustedError(DataCollectorError):
    """重试次数耗尽错误"""

    def __init__(self, message: str, max_retries: int, last_error: Optional[Exception] = None, **kwargs):
        details = {
            'max_retries': max_retries,
            'last_error': str(last_error) if last_error else None,
            'last_error_type': type(last_error).__name__ if last_error else None,
            **kwargs,
        }
        super().__init__(message, error_code='RETRY_EXHAUSTED', details=details)
        self.max_retries = max_retries
        self.last_error = last_error


class DataParsingError(DataCollectorError):
    """数据解析错误"""

    def __init__(
        self, message: str, raw_data: Optional[str] = None, parser_type: Optional[str] = None, **kwargs
    ):
        details = {
            'raw_data': raw_data[:1000] if raw_data else None,  # 限制长度避免日志过长
            'parser_type': parser_type,
            **kwargs,
        }
        super().__init__(message, error_code='PARSING_ERROR', details=details)
        self.raw_data = raw_data
        self.parser_type = parser_type


# 错误代码映射
ERROR_CODES = {
    'API_ERROR': APIError,
    'RATE_LIMIT': RateLimitError,
    'AUTH_ERROR': AuthenticationError,
    'DATA_QUALITY': DataQualityError,
    'NETWORK_ERROR': NetworkError,
    'CONFIG_ERROR': ConfigurationError,
    'SYMBOL_NOT_FOUND': SymbolNotFoundError,
    'DATA_NOT_AVAILABLE': DataNotAvailableError,
    'VALIDATION_ERROR': ValidationError,
    'RETRY_EXHAUSTED': RetryExhaustedError,
    'PARSING_ERROR': DataParsingError,
}


def create_error_from_code(error_code: str, message: str, **kwargs) -> DataCollectorError:
    """根据错误代码创建对应的异常实例"""
    error_class = ERROR_CODES.get(error_code, DataCollectorError)
    return error_class(message, **kwargs)
