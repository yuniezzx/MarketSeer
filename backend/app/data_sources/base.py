from abc import ABC, abstractmethod
from logger import logger


class BaseClient(ABC):
    def __init__(self):
        self.logger = logger

    @abstractmethod
    def fetch(self, api_name: str, params: dict = None) -> dict:
        """
        通用的数据获取接口

        Args:
            api_name: 接口名称
            params: 接口参数字典

        Returns:
            返回原始数据（可能是 DataFrame、dict 等，取决于具体API）
        """
        pass
