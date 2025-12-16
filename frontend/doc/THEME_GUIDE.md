# MarketSeer Tailwind 主题设计指南

## 🎨 设计理念

本主题专为股票检测和分析项目设计，采用专业金融风格，提供清晰的数据可视化和直观的信息展示。

## 📊 配色方案

### 主色调

- **Primary（主色）**: 专业深蓝色 - 代表信任、稳定和专业性
- **Accent（强调色）**: 金色/琥珀色 - 代表财富和价值
- **Background（背景）**: 浅蓝灰色 - 舒适的阅读背景

### 股票专用颜色

#### 涨（Bull）- 绿色系

```jsx
// 文字颜色
<span className="text-bull">+5.23%</span>

// 背景色
<div className="bg-bull text-bull-foreground">上涨</div>

// 浅色背景（用于卡片）
<div className="bg-bull-light">涨幅数据</div>

// 边框
<div className="border-2 border-bull">涨停</div>
```

#### 跌（Bear）- 红色系

```jsx
// 文字颜色
<span className="text-bear">-3.15%</span>

// 背景色
<div className="bg-bear text-bear-foreground">下跌</div>

// 浅色背景
<div className="bg-bear-light">跌幅数据</div>

// 边框
<div className="border-2 border-bear">跌停</div>
```

#### 平盘（Neutral）- 灰色系

```jsx
<span className='text-neutral-stock'>0.00%</span>
```

## 🛠️ 实用工具类

### 数据表格样式

```jsx
<table className='w-full'>
  <thead>
    <tr>
      <th className='data-table-header'>股票代码</th>
      <th className='data-table-header'>股票名称</th>
      <th className='data-table-header'>当前价格</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td className='data-table-cell'>000001</td>
      <td className='data-table-cell'>平安银行</td>
      <td className='data-table-cell mono-numbers'>12.45</td>
    </tr>
  </tbody>
</table>
```

### 价格变动动画

```jsx
// 价格上涨时（带脉动动画）
<span className="price-up mono-numbers">125.67</span>

// 价格下跌时（带脉动动画）
<span className="price-down mono-numbers">98.32</span>
```

### 图表容器

```jsx
<div className='chart-container'>
  {/* 你的图表组件 */}
  <canvas id='stockChart'></canvas>
</div>
```

### 金融数字等宽字体

确保数字对齐显示，适用于价格、百分比等数值：

```jsx
<div className='mono-numbers'>
  <p>123.45</p>
  <p>98.76</p>
  <p>1,234.56</p>
</div>
```

### 专业渐变背景

```jsx
// 深色渐变（适合 Hero 区域）
<div className="gradient-financial text-white p-8">
  <h1>MarketSeer</h1>
  <p>专业股票分析平台</p>
</div>

// 浅色渐变（适合内容区域）
<div className="gradient-financial-light p-8">
  <h2>市场概览</h2>
</div>
```

## 🎯 图表配色

使用 CSS 变量定义的 6 种图表颜色，适合多维度数据可视化：

```javascript
// 在 JavaScript 中获取图表颜色
const chartColors = [
  'oklch(0.45 0.15 264)', // chart-1: 主蓝
  'oklch(0.6 0.18 145)', // chart-2: 绿
  'oklch(0.65 0.18 25)', // chart-3: 红/橙
  'oklch(0.65 0.15 285)', // chart-4: 紫
  'oklch(0.7 0.12 85)', // chart-5: 黄/金
  'oklch(0.55 0.15 200)', // chart-6: 青
];

// 或者使用 CSS 变量
const ctx = document.getElementById('myChart');
const styles = getComputedStyle(document.documentElement);
const color1 = styles.getPropertyValue('--chart-1');
```

## 🌓 深色模式

主题自动支持深色模式，只需在根元素添加 `dark` 类：

```jsx
// React 中切换深色模式示例
function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  return <button onClick={toggleTheme}>{isDark ? '🌞 浅色' : '🌙 深色'}</button>;
}
```

## 📱 完整示例

### 股票卡片组件

```jsx
function StockCard({ stock }) {
  const isUp = stock.change >= 0;

  return (
    <div className='chart-container hover:shadow-lg transition-shadow'>
      {/* 标题 */}
      <div className='flex justify-between items-start mb-4'>
        <div>
          <h3 className='text-lg font-semibold'>{stock.name}</h3>
          <p className='text-sm text-muted-foreground'>{stock.code}</p>
        </div>
        <span className={`text-2xl font-bold mono-numbers ${isUp ? 'text-bull' : 'text-bear'}`}>{stock.price.toFixed(2)}</span>
      </div>

      {/* 涨跌幅 */}
      <div className={`inline-flex items-center px-3 py-1 rounded-full ${isUp ? 'bg-bull-light text-bull' : 'bg-bear-light text-bear'}`}>
        <span className='mono-numbers'>
          {isUp ? '+' : ''}
          {stock.change.toFixed(2)}%
        </span>
      </div>

      {/* 其他信息 */}
      <div className='mt-4 grid grid-cols-3 gap-4'>
        <div>
          <p className='text-xs text-muted-foreground'>今开</p>
          <p className='mono-numbers font-medium'>{stock.open.toFixed(2)}</p>
        </div>
        <div>
          <p className='text-xs text-muted-foreground'>最高</p>
          <p className='mono-numbers font-medium text-bull'>{stock.high.toFixed(2)}</p>
        </div>
        <div>
          <p className='text-xs text-muted-foreground'>最低</p>
          <p className='mono-numbers font-medium text-bear'>{stock.low.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
}
```

### 市场概览页面

```jsx
function MarketOverview() {
  return (
    <div className='min-h-screen bg-background'>
      {/* Hero 区域 */}
      <div className='gradient-financial text-white py-16 px-8'>
        <div className='max-w-7xl mx-auto'>
          <h1 className='text-4xl font-bold mb-4'>市场概览</h1>
          <p className='text-lg opacity-90'>实时追踪市场动态</p>
        </div>
      </div>

      {/* 数据表格 */}
      <div className='max-w-7xl mx-auto px-8 py-8'>
        <div className='bg-card rounded-lg border border-border overflow-hidden'>
          <table className='w-full'>
            <thead className='bg-muted'>
              <tr>
                <th className='data-table-header'>股票代码</th>
                <th className='data-table-header'>名称</th>
                <th className='data-table-header'>最新价</th>
                <th className='data-table-header'>涨跌幅</th>
              </tr>
            </thead>
            <tbody className='divide-y divide-border'>
              {stocks.map(stock => (
                <tr key={stock.code} className='hover:bg-muted/50 transition-colors'>
                  <td className='data-table-cell mono-numbers'>{stock.code}</td>
                  <td className='data-table-cell'>{stock.name}</td>
                  <td className='data-table-cell mono-numbers font-medium'>{stock.price.toFixed(2)}</td>
                  <td className='data-table-cell'>
                    <span className={`mono-numbers ${stock.change > 0 ? 'text-bull' : stock.change < 0 ? 'text-bear' : 'text-neutral-stock'}`}>
                      {stock.change > 0 ? '+' : ''}
                      {stock.change.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
```

## 🎨 颜色变量参考

在需要自定义样式时，可以直接使用 CSS 变量：

```css
.custom-element {
  background-color: var(--bull);
  color: var(--bull-foreground);
  border: 1px solid var(--border);
}

.custom-chart {
  stroke: var(--chart-1);
  fill: var(--chart-2);
}
```

## 💡 设计建议

1. **数字显示**: 所有价格、百分比等数字都应使用 `mono-numbers` 类，确保对齐
2. **涨跌颜色**: 始终使用 `text-bull` 和 `text-bear` 而不是直接的绿色/红色
3. **卡片布局**: 使用 `chart-container` 或组合 `bg-card border border-border rounded-lg`
4. **响应式**: 配合 Tailwind 的响应式类（sm:, md:, lg:）实现移动端适配
5. **深色模式**: 所有组件都应考虑深色模式下的显示效果

## 🚀 快速开始

1. 确保已导入 `index.css`：

```javascript
// main.jsx
import './index.css';
```

2. 开始使用主题类：

```jsx
<div className='bg-background text-foreground min-h-screen'>
  <h1 className='text-primary'>MarketSeer</h1>
  <span className='text-bull'>+5.23%</span>
</div>
```

3. 享受专业的金融数据展示效果！

---

**主题版本**: 1.0.0  
**最后更新**: 2025 年 12 月
