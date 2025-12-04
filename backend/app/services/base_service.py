"""
基础服务类定义
提供数据源访问和数据库操作的通用方法
"""

from abc import ABC
from datetime import datetime
from app.models import db
from config import Config
from logger import logger


class BaseService(ABC):
    """
    所有业务服务的抽象基类

    提供通用功能：
    - 多数据源采集（AkShare, EFinance 等）
    - 通用数据库操作
    - 统一的日志记录
    - 异常处理机制
    """

    def __init__(self):
        """初始化基础服务"""
        self.config = Config()
        self.logger = logger.bind(name=self.__class__.__name__)

    # ============ 数据源采集方法 ============

    def _fetch_from_akshare(self, api_name: str, api_params: dict = None) -> list:
        """
        通用 AkShare 数据获取函数

        Args:
            api_name (str): akshare 接口名称，如 'stock_info_a_code_name'
            api_params (dict): 传递给接口的参数字典

        Returns:
            list: 获取到的数据列表（dict 格式）
        """
        self.logger.info(f"从 AkShare 获取数据，接口: {api_name}, 参数: {api_params}")
        try:
            import akshare as ak

            # 获取接口函数
            api_func = getattr(ak, api_name, None)
            if not api_func:
                self.logger.error(f"AkShare 未找到接口: {api_name}")
                return []

            # 调用接口
            if api_params:
                df = api_func(**api_params)
            else:
                df = api_func()

            # 转换为 dict list
            if hasattr(df, 'to_dict'):
                return df.to_dict(orient='records')
            else:
                self.logger.error("AkShare 返回结果无法转换为 dict list")
                return []

        except Exception as e:
            self.logger.error(f"AkShare 数据获取失败: {str(e)}")
            return []

    def _fetch_from_efinance(self, api_name: str = None, api_params: dict = None) -> list:
        """
        从 EFinance 获取数据

        Args:
            api_name (str): efinance 接口名称（可选）
            api_params (dict): 传递给接口的参数字典

        Returns:
            list: 获取到的数据列表

        TODO: 子类根据需要实现具体的 EFinance 数据采集逻辑
        """
        self.logger.info(f"从 EFinance 获取数据，接口: {api_name}, 参数: {api_params}")

        try:
            # 示例：import efinance as ef
            # df = ef.stock.get_realtime_quotes()
            # return df.to_dict(orient='records')

            # 临时返回空列表，待子类实现
            return []
        except Exception as e:
            self.logger.error(f"EFinance 数据获取失败: {str(e)}")
            return []

    # ============ 数据库操作方法 ============

    def _save_to_db(self, model_class, data_list: list, unique_fields: list = None) -> int:
        """
        通用的数据库保存方法（批量保存或更新）

        Args:
            model_class: 模型类（如 StockInfo, DailyLHB）
            data_list (list): 要保存的数据列表
            unique_fields (list): 用于判断记录是否存在的唯一字段列表，默认为 ['code']

        Returns:
            int: 更新的记录数
        """
        if unique_fields is None:
            unique_fields = ['code']
        
        updated_count = 0

        for data in data_list:
            try:
                # 构建过滤条件
                filter_conditions = {field: data.get(field) for field in unique_fields}
                
                # 检查是否所有唯一字段都有值
                if not all(filter_conditions.values()):
                    self.logger.warning(f"数据缺少必需的唯一字段，跳过: {filter_conditions}")
                    continue

                # 查询是否已存在
                existing_record = model_class.query.filter_by(**filter_conditions).first()

                if existing_record:
                    # 更新现有记录
                    for key, value in data.items():
                        if hasattr(existing_record, key):
                            setattr(existing_record, key, value)
                    if hasattr(existing_record, "updated_at"):
                        existing_record.updated_at = datetime.now()
                else:
                    # 创建新记录
                    if hasattr(model_class, 'from_dict'):
                        new_record = model_class.from_dict(data)
                    else:
                        new_record = model_class(**data)
                    db.session.add(new_record)

                updated_count += 1

            except Exception as e:
                self.logger.error(f"保存数据失败: {str(e)}")
                continue

        # 提交事务
        try:
            db.session.commit()
            self.logger.info(f"成功保存 {updated_count} 条记录")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"数据库提交失败: {str(e)}")
            raise

        return updated_count

    def _batch_query(self, model_class, filters: dict = None, limit: int = None) -> list:
        """
        通用的批量查询方法

        Args:
            model_class: 模型类
            filters (dict): 过滤条件字典
            limit (int): 限制返回数量

        Returns:
            list: 查询结果列表
        """
        query = model_class.query

        if filters:
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)

        if limit:
            query = query.limit(limit)

        return query.all()

    # ============ 数据映射方法 ============

    def _apply_mapper(self, mapper_func, *sources, **kwargs) -> dict:
        """
        应用映射函数处理多数据源

        Args:
            mapper_func: 映射函数
            *sources: 多个数据源
            **kwargs: 关键字参数数据源

        Returns:
            dict: 映射后的数据
        """
        try:
            return mapper_func(*sources, **kwargs)
        except Exception as e:
            self.logger.error(f"数据映射失败: {str(e)}")
            return {}
