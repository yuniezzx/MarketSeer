from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from logger import logger
from app.models.base import db, BaseModel

# 定义泛型类型变量
ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    基础 Repository 类，封装通用的 CRUD 操作

    Attributes:
        model: SQLAlchemy 模型类
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化 Repository

        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model

    def create(self, **kwargs) -> Optional[ModelType]:
        """
        创建单条记录

        Args:
            **kwargs: 模型字段和值

        Returns:
            创建的模型实例，失败返回 None
        """
        try:
            instance = self.model(**kwargs)
            db.session.add(instance)
            db.session.commit()
            logger.info(f"{self.model.__name__} 创建成功: ID={instance.id}")
            return instance
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"{self.model.__name__} 创建失败: {str(e)}")
            return None

    def bulk_create(self, items: List[Dict[str, Any]]) -> bool:
        """
        批量创建记录

        Args:
            items: 字典列表，每个字典包含模型字段和值

        Returns:
            成功返回 True，失败返回 False
        """
        try:
            instances = [self.model(**item) for item in items]
            db.session.bulk_save_objects(instances)
            db.session.commit()
            logger.info(f"{self.model.__name__} 批量创建成功: 数量={len(items)}")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"{self.model.__name__} 批量创建失败: {str(e)}")
            return False

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据 ID 获取记录

        Args:
            id: 记录 ID

        Returns:
            模型实例，不存在返回 None
        """
        try:
            return db.session.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} 查询失败 (ID={id}): {str(e)}")
            return None

    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """
        根据指定字段获取单条记录

        Args:
            field: 字段名
            value: 字段值

        Returns:
            模型实例，不存在返回 None
        """
        try:
            return db.session.query(self.model).filter(getattr(self.model, field) == value).first()
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} 查询失败 ({field}={value}): {str(e)}")
            return None

    def get_all(
        self,
        offset: int = 0,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> List[ModelType]:
        """
        获取所有记录（支持分页和排序）

        Args:
            offset: 偏移量
            limit: 限制数量
            order_by: 排序字段
            desc: 是否降序

        Returns:
            模型实例列表
        """
        try:
            query = db.session.query(self.model)

            # 排序
            if order_by:
                order_field = getattr(self.model, order_by)
                query = query.order_by(order_field.desc() if desc else order_field.asc())

            # 分页
            query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} 查询所有记录失败: {str(e)}")
            return []

    def get_by_filters(
        self,
        filters: Dict[str, Any],
        offset: int = 0,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        desc: bool = False,
        use_or: bool = False,
    ) -> List[ModelType]:
        """
        根据过滤条件获取记录（支持分页和排序）

        Args:
            filters: 过滤条件字典 {field: value}
            offset: 偏移量
            limit: 限制数量
            order_by: 排序字段
            desc: 是否降序
            use_or: 是否使用 OR 逻辑（默认 AND）

        Returns:
            模型实例列表
        """
        try:
            query = db.session.query(self.model)

            # 构建过滤条件
            if filters:
                conditions = [getattr(self.model, key) == value for key, value in filters.items()]
                if use_or:
                    query = query.filter(or_(*conditions))
                else:
                    query = query.filter(and_(*conditions))

            # 排序
            if order_by:
                order_field = getattr(self.model, order_by)
                query = query.order_by(order_field.desc() if desc else order_field.asc())

            # 分页
            query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} 条件查询失败: {str(e)}")
            return []

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        统计记录数量

        Args:
            filters: 可选的过滤条件字典

        Returns:
            记录数量
        """
        try:
            query = db.session.query(self.model)

            if filters:
                conditions = [getattr(self.model, key) == value for key, value in filters.items()]
                query = query.filter(and_(*conditions))

            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} 统计失败: {str(e)}")
            return 0

    def exists(self, **kwargs) -> bool:
        """
        检查记录是否存在

        Args:
            **kwargs: 字段条件

        Returns:
            存在返回 True，否则返回 False
        """
        try:
            query = db.session.query(self.model)
            for key, value in kwargs.items():
                query = query.filter(getattr(self.model, key) == value)
            return db.session.query(query.exists()).scalar()
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} 存在性检查失败: {str(e)}")
            return False

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        根据 ID 更新记录

        Args:
            id: 记录 ID
            **kwargs: 要更新的字段和值

        Returns:
            更新后的模型实例，失败返回 None
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                logger.warning(f"{self.model.__name__} 更新失败: ID={id} 不存在")
                return None

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            db.session.commit()
            logger.info(f"{self.model.__name__} 更新成功: ID={id}")
            return instance
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"{self.model.__name__} 更新失败 (ID={id}): {str(e)}")
            return None

    def update_by_filters(self, filters: Dict[str, Any], **kwargs) -> int:
        """
        根据过滤条件批量更新记录

        Args:
            filters: 过滤条件字典
            **kwargs: 要更新的字段和值

        Returns:
            更新的记录数量
        """
        try:
            query = db.session.query(self.model)

            # 构建过滤条件
            if filters:
                conditions = [getattr(self.model, key) == value for key, value in filters.items()]
                query = query.filter(and_(*conditions))

            count = query.update(kwargs, synchronize_session=False)
            db.session.commit()
            logger.info(f"{self.model.__name__} 批量更新成功: 数量={count}")
            return count
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"{self.model.__name__} 批量更新失败: {str(e)}")
            return 0

    def delete(self, id: int) -> bool:
        """
        根据 ID 删除记录

        Args:
            id: 记录 ID

        Returns:
            成功返回 True，失败返回 False
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                logger.warning(f"{self.model.__name__} 删除失败: ID={id} 不存在")
                return False

            db.session.delete(instance)
            db.session.commit()
            logger.info(f"{self.model.__name__} 删除成功: ID={id}")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"{self.model.__name__} 删除失败 (ID={id}): {str(e)}")
            return False

    def delete_by_filters(self, filters: Dict[str, Any]) -> int:
        """
        根据过滤条件批量删除记录

        Args:
            filters: 过滤条件字典

        Returns:
            删除的记录数量
        """
        try:
            query = db.session.query(self.model)

            # 构建过滤条件
            if filters:
                conditions = [getattr(self.model, key) == value for key, value in filters.items()]
                query = query.filter(and_(*conditions))

            count = query.delete(synchronize_session=False)
            db.session.commit()
            logger.info(f"{self.model.__name__} 批量删除成功: 数量={count}")
            return count
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"{self.model.__name__} 批量删除失败: {str(e)}")
            return 0

    def upsert(self, unique_field: str, unique_value: Any, **kwargs) -> Optional[ModelType]:
        """
        插入或更新记录（如果唯一字段存在则更新，否则创建）

        Args:
            unique_field: 唯一字段名
            unique_value: 唯一字段值
            **kwargs: 其他字段和值

        Returns:
            模型实例，失败返回 None
        """
        try:
            instance = self.get_by_field(unique_field, unique_value)

            if instance:
                # 更新现有记录
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                logger.info(f"{self.model.__name__} 更新记录: {unique_field}={unique_value}")
            else:
                # 创建新记录
                kwargs[unique_field] = unique_value
                instance = self.model(**kwargs)
                db.session.add(instance)
                logger.info(f"{self.model.__name__} 创建记录: {unique_field}={unique_value}")

            db.session.commit()
            return instance
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"{self.model.__name__} upsert 失败: {str(e)}")
            return None
