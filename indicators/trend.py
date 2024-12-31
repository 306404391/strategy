from typing import Dict
import pandas as pd
import talib
from .base import BaseIndicator

class MovingAverage(BaseIndicator):
    """移动平均指标"""
    
    def __init__(self, params: Dict):
        super().__init__(params)
        self.period = params.get('period', 20)
        self.ma_type = params.get('ma_type', 'sma')
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        if not self.validate_data(data):
            return {}
            
        close = data['close']
        if self.ma_type == 'sma':
            self.values['ma'] = talib.SMA(close, timeperiod=self.period)
        elif self.ma_type == 'ema':
            self.values['ma'] = talib.EMA(close, timeperiod=self.period)
        
        return self.values
        
    def update(self, data: pd.DataFrame) -> None:
        self.calculate(data)

class BollingerBands(BaseIndicator):
    """布林带指标"""
    
    def __init__(self, params: Dict):
        super().__init__(params)
        self.period = params.get('period', 20)
        self.std_dev = params.get('std_dev', 2)
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        if not self.validate_data(data):
            return {}
            
        upper, middle, lower = talib.BBANDS(
            data['close'],
            timeperiod=self.period,
            nbdevup=self.std_dev,
            nbdevdn=self.std_dev
        )
        
        self.values.update({
            'upper': upper,
            'middle': middle,
            'lower': lower
        })
        
        return self.values
        
    def update(self, data: pd.DataFrame) -> None:
        self.calculate(data) 