from abc import ABC, abstractmethod
from logger import logger
from datetime import datetime, timedelta
from pathlib import Path
import json
import pandas as pd
from config import Config

class BaseClient(ABC):
    def __init__(self):
        self.logger = logger

    @abstractmethod
    def fetch(self, api_name: str, params: dict = None) -> dict:
        """
        通用的数据获取接口

        Args:
            api_name: 接口名称
            params: 接口参数字典

        Returns:
            返回原始数据（可能是 DataFrame、dict 等，取决于具体API）
        """
        pass

    def _save_raw_data(self, api_name: str, params: dict, data):
        """
        保存原始数据到本地文件
        
        Args:
            api_name: API 名称
            params: API 参数
            data: 原始数据(可能是 DataFrame 或其他格式)
        """
        if not Config.SAVE_RAW_DATA:
            return
        
        try:
            data_dir = Config.AKSHARE_RAW_DATA_DIR
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            symbol = params.get('symbol', params.get('stock_code', 'unknown')) if params else 'unknown'
            filename = f"{api_name}_{symbol}_{timestamp}.json"
            filepath = data_dir / filename
            
            # 转换数据格式
            if isinstance(data, pd.DataFrame):
                data_to_save = {
                    'api_name': api_name,
                    'params': params,
                    'timestamp': timestamp,
                    'data': data.to_dict(orient='records')
                }
            elif isinstance(data, dict):
                data_to_save = {
                    'api_name': api_name,
                    'params': params,
                    'timestamp': timestamp,
                    'data': data
                }
            else:
                data_to_save = {
                    'api_name': api_name,
                    'params': params,
                    'timestamp': timestamp,
                    'data': str(data)
                }
            
            # 保存为 JSON 文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Raw data saved to: {filepath}")
            
            # 清理过期文件
            self._cleanup_old_files(data_dir)
            
        except Exception as e:
            # 保存失败不影响主流程,只记录日志
            self.logger.warning(f"Failed to save raw data for {api_name}: {str(e)}")
    
    def _cleanup_old_files(self, data_dir: Path):
        """
        清理过期的原始数据文件
        
        Args:
            data_dir: 数据目录路径
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=Config.SAVE_RAW_DATA_DAYS)
            
            for file in data_dir.glob('*.json'):
                # 检查文件修改时间
                file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    file.unlink()
                    self.logger.debug(f"Deleted old raw data file: {file.name}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old files: {str(e)}")
