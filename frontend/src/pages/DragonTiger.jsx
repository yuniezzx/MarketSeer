import { useState } from 'react';
import dayjs from 'dayjs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

function DragonTiger() {
    // 计算开始日期：前两个星期，但不超过2025/12/01
    const defaultStartDate = dayjs().subtract(14, 'days');
    const cutoffDate = dayjs('2025-12-01');
    const startDateValue = defaultStartDate.isBefore(cutoffDate) ? cutoffDate : defaultStartDate;

    const [startDate, setStartDate] = useState(startDateValue.format('YYYY-MM-DD'));
    const [endDate, setEndDate] = useState(dayjs().format('YYYY-MM-DD'));
    const [daysBack, setDaysBack] = useState(7);
    const [loading, setLoading] = useState(false);
    return (
        <div className='p-6'>

            <Tabs defaultValue="daily" className="w-full">
                <TabsList className="w-fit grid grid-cols-3">
                    <TabsTrigger value="daily" className="text-sm">每日模式</TabsTrigger>
                    <TabsTrigger value="date-range" className="text-sm">日期范围模式</TabsTrigger>
                    <TabsTrigger value="summary" className="text-sm">总表模式</TabsTrigger>
                </TabsList>

                <TabsContent value="daily" className="mt-4">
                    <div className="p-6 border rounded-lg">
                        <div className="flex items-center justify-end gap-2 mb-4">
                            <Input
                                type="number"
                                value={daysBack}
                                onChange={(e) => setDaysBack(Math.max(1, parseInt(e.target.value) || 1))}
                                className="w-20"
                                disabled={loading}
                                size="sm"
                                min="1"
                                max="365"
                            />
                            <span className="text-sm text-gray-600 dark:text-gray-400">天</span>
                            <Button disabled={loading} variant="default" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white border border-blue-600">
                                {loading ? '查询中...' : `查询`}
                            </Button>
                        </div>

                        {/* 查询结果区域 */}
                        <div>
                            <p className="text-gray-600 dark:text-gray-400 text-sm">
                                设置天数后点击查询按钮查看最近N天的龙虎榜数据
                            </p>
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="date-range" className="mt-4">
                    <div className="p-6 border rounded-lg">
                        <div className="flex items-end gap-4 flex-wrap mb-4">
                            <div className="space-x-1">
                                <label className="text-sm font-medium">开始日期</label>
                                <Input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="w-40"
                                    disabled={loading}
                                    size="sm"
                                />
                            </div>
                            <div className="space-x-1">
                                <label className="text-sm font-medium">结束日期</label>
                                <Input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="w-40"
                                    disabled={loading}
                                    size="sm"
                                />
                            </div>
                            <Button disabled={loading} variant="default" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white border border-blue-600">
                                {loading ? '查询中...' : '查询'}
                            </Button>
                        </div>

                        {/* 查询结果区域 */}
                        <div className="pt-4">
                            <p className="text-gray-600 dark:text-gray-400 text-sm">
                                选择日期范围后点击查询按钮查看龙虎榜数据
                            </p>
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="summary" className="mt-4">
                    <div className="p-6 border rounded-lg">
                        <p className="text-gray-600 dark:text-gray-400 text-sm">
                            在这里显示汇总数据的表格
                        </p>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}

export default DragonTiger;
