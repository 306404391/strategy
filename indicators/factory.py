from typing import Dict, Type
from .base import BaseIndicator
from .trend import MovingAverage, BollingerBands
from .momentum import RSI, MACD
from .volatility import ATR, KeltnerChannels
import pandas as pd

class IndicatorFactory:
    """指标工厂"""
    
    _indicators: Dict[str, Type[BaseIndicator]] = {
        # 趋势指标
        'ma': MovingAverage,
        'bbands': BollingerBands,
        
        # 动量指标
        'rsi': RSI,
        'macd': MACD,
        
        # 波动率指标
        'atr': ATR,
        'kc': KeltnerChannels
    }
    
    @classmethod
    def register_indicator(cls, name: str, indicator_class: Type[BaseIndicator]) -> None:
        """注册新指标"""
        cls._indicators[name] = indicator_class
        
    @classmethod
    def create_indicator(cls, name: str, params: Dict) -> BaseIndicator:
        """创建指标实例"""
        if name not in cls._indicators:
            raise ValueError(f"Indicator {name} not found")
            
        indicator_class = cls._indicators[name]
        return indicator_class(params)
    
    @classmethod
    def get_indicator_categories(cls) -> Dict[str, list]:
        """获取指标分类"""
        return {
            'trend': ['ma', 'bbands'],
            'momentum': ['rsi', 'macd'],
            'volatility': ['atr', 'kc']
        }

class IndicatorManager:
    """指标管理器"""
    
    def __init__(self):
        self.indicators: Dict[str, BaseIndicator] = {}
        
    def add_indicator(self, name: str, params: Dict) -> None:
        """添加指标"""
        indicator = IndicatorFactory.create_indicator(name, params)
        self.indicators[name] = indicator
        
    def remove_indicator(self, name: str) -> None:
        """移除指标"""
        if name in self.indicators:
            del self.indicators[name]
            
    def get_indicator(self, name: str) -> BaseIndicator:
        """获取指标"""
        return self.indicators.get(name)
        
    def update_all(self, data: pd.DataFrame) -> None:
        """更新所有指标"""
        for indicator in self.indicators.values():
            indicator.update(data) 