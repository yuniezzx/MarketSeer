"""
路由模块

路由规范(RESTful 标准)
=======================
1. 使用名词而非动词来表示资源。例如，使用 /users 而不是 /getUsers。
2. 使用复数形式表示资源集合。例如，使用 /products 而不是 /product
3. 使用HTTP动词来表示操作：
   - GET: 用于检索资源。
    - POST: 用于创建新资源。
    - PUT: 用于更新现有资源。
    - PATCH: 用于部分更新资源。
    - DELETE: 用于删除资源。
4. 使用嵌套路由表示资源之间的层级关系。例如，/users/{userId}/orders 表示特定用户的订单。
5. 使用查询参数进行过滤、排序和分页。例如，/products?category=electronics&sort=price_asc&page=2

模块初始化
=======================
在此文件中导入并注册所有路由蓝图。
"""

from .stocks import stocks_bp
from .dragon_tiger import dragon_tiger_bp
