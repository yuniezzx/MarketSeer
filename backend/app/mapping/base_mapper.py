"""
Base Mapper

实现 API 级别的降级机制,负责数据源到模型字段的映射
"""

from typing import Dict, Any, List, Optional, Callable
import pandas as pd
from logger import logger
from ..data_sources import ClientManager


class BaseMapper:
    """
    基础映射器

    实现 API 级降级机制:
    1. 按优先级链依次尝试每个 API
    2. 每个 API 最多只调用一次
    3. 提取所有可映射的字段
    4. 检查是否还有字段缺失
    5. 有缺失且还有下一个 API 时继续尝试
    6. 增量合并结果,不覆盖已获取的字段
    """

    def __init__(
        self,
        client_manager: ClientManager,
        api_priority_chain: List[str],
        api_configs: Dict[str, Dict[str, Any]],
        api_field_mapping: Dict[str, Dict[str, str]],
        all_fields: List[str],
    ):
        """
        初始化映射器

        Args:
            client_manager: 数据源客户端管理器
            api_priority_chain: API 优先级链,如 ['api1', 'api2', 'api3']
            api_configs: API 配置,包含 data_source, param_mapping, param_transformer
            api_field_mapping: API 字段映射,定义每个 API 返回数据到模型字段的映射
            all_fields: 所有支持的字段列表
        """
        self.client_manager = client_manager
        self.api_priority_chain = api_priority_chain
        self.api_configs = api_configs
        self.api_field_mapping = api_field_mapping
        self.all_fields = all_fields
        self.logger = logger

    def map_all_fields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        映射所有字段,使用 API 级降级机制

        Args:
            params: 调用参数,如 {'symbol': '002156'}

        Returns:
            映射结果字典,包含所有成功获取的字段

        工作流程:
            1. 按优先级链依次尝试每个 API
            2. 调用 API 并提取所有可映射字段
            3. 增量合并到结果中(不覆盖已有字段)
            4. 检查是否还有缺失字段
            5. 无缺失或无更多 API 时停止
        """
        result = {}
        missing_fields = set(self.all_fields)

        for api_name in self.api_priority_chain:
            if not missing_fields:
                # 所有字段都已获取,无需继续
                self.logger.info(f"所有字段已完整,停止降级。当前API: {api_name}")
                break

            self.logger.info(
                f"尝试 API: {api_name}, " f"缺失字段数: {len(missing_fields)}, " f"缺失字段: {missing_fields}"
            )

            # 调用 API
            data = self._call_api(api_name, params)
            if data is None:
                self.logger.warning(f"API {api_name} 调用失败,尝试下一个")
                continue

            # 提取该 API 可映射的字段
            extracted = self._extract_fields(api_name, data, missing_fields)

            if extracted:
                # 增量合并结果(不覆盖已有字段)
                for field, value in extracted.items():
                    if field not in result:  # 只添加新字段
                        result[field] = value
                        missing_fields.discard(field)

                self.logger.info(f"API {api_name} 成功提取 {len(extracted)} 个字段: {list(extracted.keys())}")
            else:
                self.logger.warning(f"API {api_name} 未提取到任何字段")

        # 记录最终结果
        if missing_fields:
            self.logger.warning(f"降级完成,仍有 {len(missing_fields)} 个字段缺失: {missing_fields}")
        else:
            self.logger.info("降级完成,所有字段均已获取")

        return result

    def _call_api(self, api_name: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        调用 API 并进行参数转换

        Args:
            api_name: API 名称
            params: 原始参数

        Returns:
            API 返回的数据,失败时返回 None

        处理流程:
            1. 获取 API 配置
            2. 转换参数格式(如添加市场前缀)
            3. 映射参数名(如 symbol -> stock_code)
            4. 调用对应的数据源客户端
        """
        try:
            config = self.api_configs.get(api_name)
            if not config:
                self.logger.error(f"API {api_name} 配置不存在")
                return None

            data_source = config['data_source']
            param_mapping = config.get('param_mapping', {})
            param_transformer: Callable[[str], str] = config.get('param_transformer')

            # 转换参数
            transformed_params = {}
            for input_key, api_key in param_mapping.items():
                if input_key in params:
                    value = params[input_key]
                    # 如果有参数转换器,进行转换
                    if param_transformer and isinstance(value, str):
                        value = param_transformer(value)
                    transformed_params[api_key] = value

            self.logger.debug(
                f"调用 API: {api_name}, "
                f"数据源: {data_source}, "
                f"原始参数: {params}, "
                f"转换后参数: {transformed_params}"
            )

            # 调用数据源客户端
            client = self.client_manager.get_client(data_source)
            data = client.fetch(api_name, transformed_params)

            return data

        except Exception as e:
            self.logger.error(f"调用 API {api_name} 时出错: {e}", exc_info=True)
            return None

    def _extract_fields(self, api_name: str, data: Any, fields: set) -> Dict[str, Any]:
        """
        从 API 数据中提取指定字段

        Args:
            api_name: API 名称
            data: API 返回的数据
            fields: 需要提取的字段集合

        Returns:
            提取的字段字典

        处理流程:
            1. 获取该 API 的字段映射配置
            2. 遍历需要提取的字段
            3. 根据映射路径从数据中获取值
            4. 返回成功提取的字段
        """
        field_mapping = self.api_field_mapping.get(api_name)
        if not field_mapping:
            self.logger.warning(f"API {api_name} 没有字段映射配置")
            return {}

        result = {}
        for field in fields:
            if field not in field_mapping:
                continue

            field_path = field_mapping[field]
            value = self._get_field_value(data, field_path)

            if value is not None:
                result[field] = value

        return result

    def _get_field_value(self, data: Any, field_path: str) -> Optional[Any]:
        """
        从数据中获取字段值,支持 DataFrame 和 dict

        Args:
            data: 数据对象(DataFrame 或 dict)
            field_path: 字段路径,支持嵌套如 'data.stock_code'

        Returns:
            字段值,不存在或为空时返回 None

        处理逻辑:
            - DataFrame: 取第一行对应列的值
            - dict: 支持嵌套路径访问
        """
        try:
            if isinstance(data, pd.DataFrame):
                # DataFrame: 取第一行
                if data.empty:
                    return None

                if field_path in data.columns:
                    value = data.iloc[0][field_path]
                    # 处理 pandas 的 NaN/None
                    if pd.isna(value):
                        return None
                    return value
                return None

            elif isinstance(data, dict):
                # dict: 支持嵌套路径
                keys = field_path.split('.')
                current = data
                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return None
                return current if current else None

            else:
                self.logger.warning(f"不支持的数据类型: {type(data)}")
                return None

        except Exception as e:
            self.logger.error(f"获取字段 {field_path} 时出错: {e}")
            return None
