✨ 项目结构

```
app/
  router/               # 路由
  service/              # 业务逻辑
  data_sources/         # 外部 API/数据获取
  repository/           # 数据库 CURD
  schemas/              # Pydantic 数据结构（输入、输出、清洗后的格式）
  mappers/              # 数据源 -> 内部结构 -> DB 的转换
  models/               # SQLAlchemy models
  utils/                # 工具
  config/               # 配置
```

📌 流程：

router 接收请求

调 service

service 调用 data_sources 拿原始数据

用 schemas 验证

用 mappers 将“第三方数据 → 内部数据 → DB model”

用 repository 写入数据库

return output
