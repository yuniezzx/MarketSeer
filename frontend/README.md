# MarketSeer Frontend

MarketSeer 前端应用 - 基于 React 和 Vite 构建的现代化金融数据可视化平台

## 技术栈

- **框架**: React 18
- **构建工具**: Vite 5
- **路由**: React Router v6
- **UI 组件**: Ant Design 5
- **HTTP 客户端**: Axios
- **图表库**: Recharts

## 项目结构

```
frontend/
├── src/
│   ├── components/      # 公共组件
│   │   └── Layout.jsx   # 布局组件
│   ├── pages/           # 页面组件
│   │   ├── HomePage.jsx
│   │   ├── StockListPage.jsx
│   │   └── StockDetailPage.jsx
│   ├── services/        # API 服务
│   │   └── api.js
│   ├── hooks/           # 自定义 Hooks（待扩展）
│   ├── utils/           # 工具函数（待扩展）
│   ├── App.jsx          # 应用根组件
│   ├── main.jsx         # 应用入口
│   └── index.css        # 全局样式
├── public/              # 静态资源
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置
└── package.json         # 项目配置
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 4. 预览生产构建

```bash
npm run preview
```

## 可用脚本

- `npm run dev` - 启动开发服务器
- `npm run build` - 构建生产版本
- `npm run preview` - 预览生产构建
- `npm run lint` - 运行代码检查

## 功能特性

### 已实现

- ✅ 首页展示
- ✅ 股票列表查询（支持分页）
- ✅ 股票搜索功能
- ✅ 股票详情页面
- ✅ 响应式布局
- ✅ API 代理配置

### 待实现

- ⏳ 数据可视化图表
- ⏳ 股票价格走势图
- ⏳ 财务数据展示
- ⏳ 行业分析
- ⏳ 用户偏好设置
- ⏳ 数据导出功能

## API 集成

前端通过 Axios 与后端 API 通信，所有 API 请求通过 Vite 代理转发到后端服务：

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  }
}
```

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建新的页面组件
2. 在 `src/App.jsx` 中添加路由配置
3. 在导航菜单中添加入口（如需要）

### 添加新的 API 接口

1. 在 `src/services/api.js` 中添加新的 API 方法
2. 在组件中导入并使用

### 样式规范

- 使用 CSS Modules 或独立的 CSS 文件
- 遵循 Ant Design 的设计规范
- 保持组件样式的模块化

## 环境要求

- Node.js >= 16
- npm >= 8

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 许可证

MIT License
