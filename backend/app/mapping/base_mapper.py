"""
Base Mapper

实现字段级别的多源降级机制,负责数据源到模型字段的映射
"""

from typing import Dict, Any, List, Optional
from logger import logger
from ..data_sources import ClientManager


class BaseMapper:
    """
    基础映射器

    负责根据配置将多个数据源的数据映射到模型字段,实现字段级别的降级机制
    """

    def __init__(
        self,
        client_manager: ClientManager,
        field_mapping: Dict[str, List[Dict[str, Any]]],
        api_configs: Dict[str, Dict[str, Any]],
    ):
        """
        初始化映射器

        Args:
            client_manager: 数据源客户端管理器
            field_mapping: 字段映射配置,格式为 {model_field: [fallback_chain]}
            api_configs: API配置,包含每个API的数据源和参数映射
        """
        self.client_manager = client_manager
        self.field_mapping = field_mapping
        self.api_configs = api_configs
        self.logger = logger

    def map_field(self, model_field: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        映射单个字段,按照降级链逐个尝试数据源

        Args:
            model_field: 模型字段名
            params: 查询参数(如 symbol)

        Returns:
            字段值,如果所有数据源都失败则返回 None
        """
        if model_field not in self.field_mapping:
            self.logger.warning(f"Field '{model_field}' not found in mapping configuration")
            return None

        fallback_chain = self.field_mapping[model_field]

        for fallback_config in fallback_chain:
            api_name = fallback_config['api']
            source_field = fallback_config['field']
            transform_func = fallback_config.get('transform')

            try:
                # 获取API配置
                if api_name not in self.api_configs:
                    self.logger.error(f"API '{api_name}' not found in API configs")
                    continue

                api_config = self.api_configs[api_name]
                data_source = api_config['data_source']
                param_mapping = api_config.get('param_mapping', {})

                # 映射参数
                mapped_params = {}
                for api_param, input_param in param_mapping.items():
                    if input_param in params:
                        mapped_params[api_param] = params[input_param]
                    else:
                        self.logger.warning(f"Required parameter '{input_param}' not found in input params")
                        raise ValueError(f"Missing required parameter: {input_param}")

                # 获取客户端
                client = self.client_manager.get_client(data_source)

                # 调用API
                self.logger.debug(f"Trying to fetch field '{model_field}' from {data_source}.{api_name}")
                raw_data = client.fetch(api_name, mapped_params)

                # 提取字段值
                value = self._extract_value(raw_data, source_field)

                # 应用转换函数
                if value is not None and transform_func is not None:
                    value = transform_func(value)

                # 如果成功获取到值,返回
                if value is not None:
                    self.logger.info(
                        f"Successfully fetched field '{model_field}' from {data_source}.{api_name}"
                    )
                    return value
                else:
                    self.logger.warning(
                        f"Field '{source_field}' is None in response from {data_source}.{api_name}"
                    )

            except Exception as e:
                self.logger.error(f"Error fetching field '{model_field}' from {api_name}: {str(e)}")
                continue

        self.logger.error(f"All fallback options failed for field '{model_field}'")
        return None

    def _extract_value(self, raw_data: Any, field_path: str) -> Optional[Any]:
        """
        从原始数据中提取字段值

        支持点号分隔的路径,如 'data.name' 或简单字段名 'name'

        Args:
            raw_data: 原始数据(可能是dict, DataFrame等)
            field_path: 字段路径

        Returns:
            字段值,如果找不到返回 None
        """
        try:
            # 处理 pandas DataFrame
            if hasattr(raw_data, 'iloc'):
                # DataFrame: 获取第一行数据
                if len(raw_data) == 0:
                    return None
                if field_path in raw_data.columns:
                    value = raw_data.iloc[0][field_path]
                    # 处理 pandas 的 NaN/NaT
                    import pandas as pd

                    if pd.isna(value):
                        return None
                    return value
                return None

            # 处理 dict
            if isinstance(raw_data, dict):
                # 支持点号分隔的路径
                keys = field_path.split('.')
                current = raw_data
                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return None
                return current

            return None

        except Exception as e:
            self.logger.error(f"Error extracting field '{field_path}': {str(e)}")
            return None

    def map_all_fields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        映射所有配置的字段

        Args:
            params: 查询参数

        Returns:
            映射后的字段字典
        """
        result = {}
        for model_field in self.field_mapping.keys():
            value = self.map_field(model_field, params)
            if value is not None:
                result[model_field] = value
        return result
