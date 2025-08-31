"""
股票基本信息存储服务

提供股票基本信息的数据库CRUD操作，包括：
- 保存股票信息
- 查询股票信息
- 更新股票信息
- 批量操作
- 数据备份
"""

import json
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..collectors.data_types import StockInfo
from .database import DatabaseManager
from ...utils.logger import get_database_logger


class StockInfoStorage:
    """股票基本信息存储服务类"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        初始化存储服务

        Args:
            db_manager: 数据库管理器，如果不提供则创建新实例
        """
        self.db_manager = db_manager or DatabaseManager()
        self.logger = get_database_logger()
        self.backup_dir = Path("data/raw/stocks")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def save_stock_info(self, stock_info: StockInfo, backup: bool = True) -> bool:
        """
        保存股票基本信息

        Args:
            stock_info: 股票信息对象
            backup: 是否备份到文件系统

        Returns:
            bool: 保存是否成功
        """
        try:
            # 转换为数据库记录格式
            record = self._stock_info_to_record(stock_info)

            # 检查是否已存在
            existing = self.get_stock_info(stock_info.symbol)

            if existing:
                # 更新现有记录
                success = self._update_stock_record(stock_info.symbol, record)
                operation = "更新"
            else:
                # 插入新记录
                success = self._insert_stock_record(record)
                operation = "插入"

            if success:
                self.logger.info(f"成功{operation}股票信息: {stock_info.symbol} - {stock_info.name}")

                # 备份到文件系统
                if backup:
                    self._backup_to_file(stock_info)

                return True
            else:
                self.logger.error(f"失败{operation}股票信息: {stock_info.symbol}")
                return False

        except Exception as e:
            self.logger.error(f"保存股票信息时发生错误: {e}")
            return False

    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """
        根据股票代码查询股票信息

        Args:
            symbol: 股票代码

        Returns:
            StockInfo: 股票信息对象，如果不存在返回None
        """
        try:
            query = "SELECT * FROM stocks WHERE symbol = %s"
            result = self.db_manager.fetch_one(query, (symbol,))

            if result:
                return self._record_to_stock_info(result)
            else:
                return None

        except Exception as e:
            self.logger.error(f"查询股票信息时发生错误: {e}")
            return None

    def update_stock_info(self, symbol: str, stock_info: StockInfo) -> bool:
        """
        更新股票信息

        Args:
            symbol: 股票代码
            stock_info: 新的股票信息

        Returns:
            bool: 更新是否成功
        """
        try:
            record = self._stock_info_to_record(stock_info)
            return self._update_stock_record(symbol, record)

        except Exception as e:
            self.logger.error(f"更新股票信息时发生错误: {e}")
            return False

    def batch_save_stocks(self, stocks: List[StockInfo], backup: bool = True) -> Dict[str, Any]:
        """
        批量保存股票信息

        Args:
            stocks: 股票信息列表
            backup: 是否备份

        Returns:
            Dict: 包含成功、失败统计的结果
        """
        result = {'total': len(stocks), 'success': 0, 'failed': 0, 'failed_symbols': [], 'errors': []}

        for stock_info in stocks:
            try:
                if self.save_stock_info(stock_info, backup=backup):
                    result['success'] += 1
                else:
                    result['failed'] += 1
                    result['failed_symbols'].append(stock_info.symbol)

            except Exception as e:
                result['failed'] += 1
                result['failed_symbols'].append(stock_info.symbol)
                result['errors'].append(f"{stock_info.symbol}: {str(e)}")

        self.logger.info(
            f"批量保存完成: 总计{result['total']}, 成功{result['success']}, 失败{result['failed']}"
        )
        return result

    def search_stocks(
        self,
        name_pattern: Optional[str] = None,
        exchange: Optional[str] = None,
        industry: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 100,
    ) -> List[StockInfo]:
        """
        搜索股票信息

        Args:
            name_pattern: 股票名称模糊搜索
            exchange: 交易所筛选
            industry: 行业筛选
            is_active: 是否活跃
            limit: 返回结果限制

        Returns:
            List[StockInfo]: 匹配的股票信息列表
        """
        try:
            conditions = []
            params = []

            if name_pattern:
                conditions.append("name LIKE %s")
                params.append(f"%{name_pattern}%")

            if exchange:
                conditions.append("exchange = %s")
                params.append(exchange)

            if industry:
                conditions.append("industry = %s")
                params.append(industry)

            if is_active is not None:
                conditions.append("is_active = %s")
                params.append(is_active)

            where_clause = " AND ".join(conditions) if conditions else "1=1"
            query = f"SELECT * FROM stocks WHERE {where_clause} ORDER BY symbol LIMIT %s"
            params.append(limit)

            results = self.db_manager.fetch_all(query, params)
            return [self._record_to_stock_info(record) for record in results]

        except Exception as e:
            self.logger.error(f"搜索股票信息时发生错误: {e}")
            return []

    def get_stock_count(self) -> int:
        """
        获取数据库中股票总数

        Returns:
            int: 股票总数
        """
        try:
            result = self.db_manager.fetch_one("SELECT COUNT(*) as count FROM stocks")
            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"获取股票总数时发生错误: {e}")
            return 0

    def delete_stock(self, symbol: str) -> bool:
        """
        删除股票信息

        Args:
            symbol: 股票代码

        Returns:
            bool: 删除是否成功
        """
        try:
            query = "DELETE FROM stocks WHERE symbol = %s"
            rows_affected = self.db_manager.execute(query, (symbol,))

            if rows_affected > 0:
                self.logger.info(f"成功删除股票信息: {symbol}")
                return True
            else:
                self.logger.warning(f"股票不存在，无法删除: {symbol}")
                return False

        except Exception as e:
            self.logger.error(f"删除股票信息时发生错误: {e}")
            return False

    def _stock_info_to_record(self, stock_info: StockInfo) -> Dict[str, Any]:
        """将StockInfo对象转换为数据库记录格式"""
        return {
            'symbol': stock_info.symbol,
            'name': stock_info.name,
            'exchange': stock_info.exchange,
            'market': stock_info.market,
            'industry': stock_info.industry,
            'sector': stock_info.sector,
            'list_date': stock_info.list_date,
            'delist_date': stock_info.delist_date,
            'is_active': stock_info.is_active,
            'currency': stock_info.currency,
            'market_cap': stock_info.market_cap,
            'shares_outstanding': stock_info.shares_outstanding,
            'description': stock_info.description,
            'website': stock_info.website,
            'data_source': 'mixed',  # 可以根据需要设置
        }

    def _record_to_stock_info(self, record: Dict[str, Any]) -> StockInfo:
        """将数据库记录转换为StockInfo对象"""
        return StockInfo(
            symbol=record['symbol'],
            name=record['name'],
            exchange=record['exchange'] or '',
            market=record['market'] or '',
            industry=record.get('industry'),
            sector=record.get('sector'),
            list_date=record.get('list_date'),
            delist_date=record.get('delist_date'),
            is_active=bool(record.get('is_active', True)),
            currency=record.get('currency', 'CNY'),
            market_cap=record.get('market_cap'),
            shares_outstanding=record.get('shares_outstanding'),
            description=record.get('description'),
            website=record.get('website'),
            metadata={
                'data_source': record.get('data_source'),
                'created_at': record.get('created_at'),
                'updated_at': record.get('updated_at'),
            },
        )

    def _insert_stock_record(self, record: Dict[str, Any]) -> bool:
        """插入新的股票记录"""
        columns = list(record.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO stocks ({', '.join(columns)}) VALUES ({placeholders})"

        rows_affected = self.db_manager.execute(query, list(record.values()))
        return rows_affected > 0

    def _update_stock_record(self, symbol: str, record: Dict[str, Any]) -> bool:
        """更新现有股票记录"""
        # 移除symbol字段，因为它是WHERE条件
        update_record = {k: v for k, v in record.items() if k != 'symbol'}

        set_clause = ', '.join([f"{col} = %s" for col in update_record.keys()])
        query = f"UPDATE stocks SET {set_clause} WHERE symbol = %s"

        params = list(update_record.values()) + [symbol]
        rows_affected = self.db_manager.execute(query, params)
        return rows_affected > 0

    def _backup_to_file(self, stock_info: StockInfo):
        """备份股票信息到文件系统"""
        try:
            backup_file = self.backup_dir / f"{stock_info.symbol}.json"

            # 准备备份数据
            backup_data = {
                'symbol': stock_info.symbol,
                'name': stock_info.name,
                'exchange': stock_info.exchange,
                'market': stock_info.market,
                'industry': stock_info.industry,
                'sector': stock_info.sector,
                'list_date': stock_info.list_date.isoformat() if stock_info.list_date else None,
                'delist_date': stock_info.delist_date.isoformat() if stock_info.delist_date else None,
                'is_active': stock_info.is_active,
                'currency': stock_info.currency,
                'market_cap': stock_info.market_cap,
                'shares_outstanding': stock_info.shares_outstanding,
                'description': stock_info.description,
                'website': stock_info.website,
                'metadata': stock_info.metadata,
                'backup_time': datetime.now().isoformat(),
            }

            # 写入文件
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            self.logger.debug(f"股票信息已备份到文件: {backup_file}")

        except Exception as e:
            self.logger.warning(f"备份股票信息到文件失败: {e}")

    def is_connected(self) -> bool:
        """
        检查数据库连接状态

        Returns:
            bool: 连接状态
        """
        try:
            if self.db_manager and self.db_manager.connection:
                # 执行简单查询测试连接
                self.db_manager.fetch_one("SELECT 1")
                return True
        except Exception as e:
            self.logger.warning(f"数据库连接检查失败: {e}")
        return False

    def list_all_symbols(self) -> List[str]:
        """
        获取所有股票代码列表

        Returns:
            List[str]: 股票代码列表
        """
        try:
            query = "SELECT symbol FROM stocks WHERE is_active = 1 ORDER BY symbol"
            results = self.db_manager.fetch_all(query)
            return [row['symbol'] for row in results] if results else []
        except Exception as e:
            self.logger.error(f"获取股票代码列表时发生错误: {e}")
            return []

    def close(self):
        """关闭数据库连接"""
        if self.db_manager:
            self.db_manager.close()
