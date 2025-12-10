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

    def _fetch_api(self, api_name: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        调用单个 API 获取原始数据

        Args:
            api_name: API 名称
            params: 查询参数

        Returns:
            API 返回的原始数据,失败返回 None
        """
        try:
            # 获取API配置
            if api_name not in self.api_configs:
                self.logger.error(f"API '{api_name}' not found in API configs")
                return None

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
            self.logger.debug(f"Fetching data from {data_source}.{api_name} with params {mapped_params}")
            raw_data = client.fetch(api_name, mapped_params)
            
            if raw_data is not None:
                self.logger.info(f"Successfully fetched data from {data_source}.{api_name}")
            else:
                self.logger.warning(f"No data returned from {data_source}.{api_name}")
            
            return raw_data

        except Exception as e:
            self.logger.error(f"Error fetching from API '{api_name}': {str(e)}")
            return None

    def map_all_fields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        映射所有配置的字段,优化后按 API 分组调用,避免重复请求

        实现逻辑:
        1. 按优先级遍历(第一优先级、第二优先级...)
        2. 对于每个优先级,收集所有需要调用的 API(去重)
        3. 批量调用这些 API 并缓存结果
        4. 从缓存结果中提取所有可以提取的字段
        5. 对于仍缺失的字段,进入下一优先级

        Args:
            params: 查询参数

        Returns:
            映射后的字段字典
        """
        result = {}
        # 记录还需要获取的字段
        pending_fields = set(self.field_mapping.keys())
        
        # 计算最大优先级深度
        max_depth = max(len(chain) for chain in self.field_mapping.values())
        
        # 按优先级逐层处理
        for priority_index in range(max_depth):
            if not pending_fields:
                # 所有字段都已获取
                break
            
            # API 调用缓存: {api_name: raw_data}
            api_cache = {}
            
            # 收集当前优先级需要调用的 API
            apis_to_fetch = set()
            for field in pending_fields:
                fallback_chain = self.field_mapping[field]
                if priority_index < len(fallback_chain):
                    api_name = fallback_chain[priority_index]['api']
                    apis_to_fetch.add(api_name)
            
            # 批量调用所有需要的 API
            self.logger.debug(
                f"Priority {priority_index + 1}: Fetching {len(apis_to_fetch)} unique APIs for {len(pending_fields)} pending fields"
            )
            for api_name in apis_to_fetch:
                raw_data = self._fetch_api(api_name, params)
                if raw_data is not None:
                    api_cache[api_name] = raw_data
            
            # 从缓存中提取所有可以提取的字段
            successfully_fetched = []
            for field in list(pending_fields):
                fallback_chain = self.field_mapping[field]
                if priority_index >= len(fallback_chain):
                    # 该字段的降级链已用尽
                    continue
                
                fallback_config = fallback_chain[priority_index]
                api_name = fallback_config['api']
                source_field = fallback_config['field']
                transform_func = fallback_config.get('transform')
                
                # 检查缓存中是否有该 API 的数据
                if api_name in api_cache:
                    raw_data = api_cache[api_name]
                    
                    # 提取字段值
                    value = self._extract_value(raw_data, source_field)
                    
                    # 应用转换函数
                    if value is not None and transform_func is not None:
                        try:
                            value = transform_func(value)
                        except Exception as e:
                            self.logger.error(
                                f"Error applying transform for field '{field}': {str(e)}"
                            )
                            value = None
                    
                    # 如果成功获取到值,记录并标记为已完成
                    if value is not None:
                        result[field] = value
                        successfully_fetched.append(field)
                        self.logger.debug(
                            f"Field '{field}' successfully fetched from API '{api_name}' at priority {priority_index + 1}"
                        )
                    else:
                        self.logger.debug(
                            f"Field '{source_field}' is None in response from API '{api_name}'"
                        )
            
            # 从待处理集合中移除已成功获取的字段
            for field in successfully_fetched:
                pending_fields.remove(field)
            
            self.logger.info(
                f"Priority {priority_index + 1}: Successfully fetched {len(successfully_fetched)} fields, "
                f"{len(pending_fields)} fields still pending"
            )
        
        # 记录最终未能获取的字段
        if pending_fields:
            self.logger.warning(
                f"Failed to fetch {len(pending_fields)} fields after trying all priorities: {pending_fields}"
            )
        
        return result
