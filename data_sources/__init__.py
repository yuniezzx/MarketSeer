# -*- coding: utf-8 -*-
# 仅用于导出“获得数据”的函数（AkShare 直连，返回原始 DataFrame）

from .akshare_client import (
    # 行情
    get_sh_a_spot,
    get_zh_a_spot,

    # 基础资料
    get_profile_em,
    get_profile_xq,

    # 龙虎榜

)

__all__ = [
    # 行情
    "get_sh_a_spot",
    "get_zh_a_spot",

    # 基础资料
    "get_profile_em",
    "get_profile_xq",

    # 龙虎榜

]
