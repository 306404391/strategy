from typing import Dict
import pandas as pd
import talib
from .base import BaseIndicator

class ATR(BaseIndicator):
    """平均真实波幅"""
    
    def __init__(self, params: Dict):
        super().__init__(params)
        self.period = params.get('period', 14)
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        if not self.validate_data(data):
            return {}
            
        self.values['atr'] = talib.ATR(
            data['high'],
            data['low'],
            data['close'],
            timeperiod=self.period
        )
        return self.values

class KeltnerChannels(BaseIndicator):
    """肯特纳通道"""
    
    def __init__(self, params: Dict):
        super().__init__(params)
        self.ema_period = params.get('ema_period', 20)
        self.atr_period = params.get('atr_period', 10)
        self.atr_multiplier = params.get('atr_multiplier', 2.0)
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        if not self.validate_data(data):
            return {}
            
        # 计算EMA
        middle = talib.EMA(data['close'], timeperiod=self.ema_period)
        
        # 计算ATR
        atr = talib.ATR(
            data['high'],
            data['low'],
            data['close'],
            timeperiod=self.atr_period
        )
        
        # 计算通道
        upper = middle + (atr * self.atr_multiplier)
        lower = middle - (atr * self.atr_multiplier)
        
        self.values.update({
            'upper': upper,
            'middle': middle,
            'lower': lower
        })
        
        return self.values 