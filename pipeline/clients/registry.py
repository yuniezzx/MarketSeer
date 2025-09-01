"""
pipeline.clients.registry
注册表：名称 -> DataClient 类/工厂，按需返回实例。
"""

from typing import Dict, Type, Optional, Callable
from threading import Lock
from .base import DataClient

_CLIENTS: Dict[str, Type[DataClient]] = {}
_INSTANCE_CACHE: Dict[str, DataClient] = {}
_LOCK = Lock()


def register(name: str) -> Callable[[Type[DataClient]], Type[DataClient]]:
    """装饰器注册：@register("akshare") class AkshareClient(DataClient): ..."""

    def decorator(cls: Type[DataClient]) -> Type[DataClient]:
        _CLIENTS[name] = cls
        return cls

    return decorator


def register_explicit(name: str, cls: Type[DataClient]) -> None:
    """显式注册：register_explicit('efinance', EfinanceClient)"""
    _CLIENTS[name] = cls


def get_client(name: str, config: Optional[dict] = None, use_cache: bool = False) -> DataClient:
    """
    返回 client 实例。

    Args:
        name: 注册名
        config: 传给构造函数的 config
        use_cache: 若 True，则第一次创建后缓存并返回同一实例（单例模式）
    """
    cls = _CLIENTS.get(name)
    if cls is None:
        raise KeyError(f"unknown client: {name}")

    if use_cache:
        with _LOCK:
            inst = _INSTANCE_CACHE.get(name)
            if inst is None:
                inst = cls(config=config or {})
                _INSTANCE_CACHE[name] = inst
            return inst
    return cls(config=config or {})


def list_clients() -> list:
    """返回已注册的 client 名称列表"""
    return list(_CLIENTS.keys())


def clear_cache(name: Optional[str] = None) -> None:
    """清理缓存（按 name 或全部）"""
    with _LOCK:
        if name:
            _INSTANCE_CACHE.pop(name, None)
        else:
            _INSTANCE_CACHE.clear()


# 尝试自动注册已存在的实现（非强制）
# 这里尽量导入已实现的 client，并注册它们；导入失败则忽略，
# 程序入口仍然可以通过 register_explicit 手动注册。
try:
    from .akshare_client import AkshareClient  # type: ignore

    register("akshare")(AkshareClient)
except Exception:
    pass

try:
    from .efinance_client import EfinanceClient  # type: ignore

    register("efinance")(EfinanceClient)
except Exception:
    pass

__all__ = ["register", "register_explicit", "get_client", "list_clients", "clear_cache"]
