import { useState, useEffect } from 'react';
import { getStocks, addStock } from '../api/stocks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function StockList() {
  const [stocks, setStocks] = useState([]);
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 页面首次加载时自动获取股票
  useEffect(() => {
    handleGetStocks();
  }, []);

  // 获取所有股票
  const handleGetStocks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getStocks();
      if (response.status === 'success') {
        setStocks(response.data);
      } else {
        setError(response.message || '获取股票列表失败');
      }
    } catch (err) {
      setError(err.message || '获取股票列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加股票
  const handleAddStock = async () => {
    if (!symbol.trim()) {
      setError('请输入股票代码');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await addStock(symbol);
      if (response.status === 'success') {
        setSymbol('');
        // 添加成功后重新获取列表
        await handleGetStocks();
      } else {
        setError(response.message || '添加股票失败');
      }
    } catch (err) {
      setError(err.message || '添加股票失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='p-6'>
      {/* 操作按钮区域 */}
      <div className='flex items-center justify-end gap-3 mb-6'>
        <Input
          size='sm'
          placeholder='输入股票代码 (如: 600000)'
          value={symbol}
          onChange={e => setSymbol(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleAddStock()}
          className='max-w-xs'
          disabled={loading}
        />
        <Button onClick={handleAddStock} disabled={loading} variant='outline' size='sm'>
          添加股票
        </Button>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className='bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded mb-4 flex items-center justify-between'>
          <span>{error}</span>
          <Button onClick={handleGetStocks} disabled={loading} variant='outline' size='sm'>
            {loading ? '加载中...' : '获取所有股票'}
          </Button>
        </div>
      )}

      {/* 股票列表表格 */}
      {stocks.length > 0 ? (
        <div className='border rounded-lg'>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>股票代码</TableHead>
                <TableHead>股票名称</TableHead>
                <TableHead>市场</TableHead>
                <TableHead>行业</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>跟踪</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stocks.map(stock => (
                <TableRow key={stock.code}>
                  <TableCell className='font-medium'>{stock.code}</TableCell>
                  <TableCell>{stock.name}</TableCell>
                  <TableCell>{stock.market}</TableCell>
                  <TableCell>{stock.industry || '-'}</TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        stock.status === 'active' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200'
                      }`}>
                      {stock.status}
                    </span>
                  </TableCell>
                  <TableCell>{stock.tracking ? <span className='text-green-600 dark:text-green-400'>✓</span> : <span className='text-gray-400'>-</span>}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : (
        <div className='text-center py-12 text-gray-500 dark:text-gray-400'>{loading ? '加载中...' : '暂无股票数据'}</div>
      )}
    </div>
  );
}

export default StockList;
