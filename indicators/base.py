from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

class IIndicator(ABC):
    """指标接口"""
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """计算指标值"""
        pass
        
    @abstractmethod
    def update(self, data: pd.DataFrame) -> None:
        """更新指标值"""
        pass

class BaseIndicator(IIndicator):
    """指标基类"""
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.values: Dict[str, pd.Series] = {}
        
    def validate_data(self, data: pd.DataFrame) -> bool:
        """验证数据有效性"""
        if data is None or len(data) == 0:
            return False
        return True
        
    def get_value(self, name: str, index: int = -1) -> Optional[float]:
        """获取指标值"""
        if name not in self.values:
            return None
        series = self.values[name]
        if len(series) <= abs(index):
            return None
        return series.iloc[index] 