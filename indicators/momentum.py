from typing import Dict
import pandas as pd
import talib
from .base import BaseIndicator

class RSI(BaseIndicator):
    """相对强弱指标"""
    
    def __init__(self, params: Dict):
        super().__init__(params)
        self.period = params.get('period', 14)
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        if not self.validate_data(data):
            return {}
            
        self.values['rsi'] = talib.RSI(data['close'], timeperiod=self.period)
        return self.values
        
    def update(self, data: pd.DataFrame) -> None:
        self.calculate(data)

class MACD(BaseIndicator):
    """MACD指标"""
    
    def __init__(self, params: Dict):
        super().__init__(params)
        self.fast_period = params.get('fast_period', 12)
        self.slow_period = params.get('slow_period', 26)
        self.signal_period = params.get('signal_period', 9)
        
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        if not self.validate_data(data):
            return {}
            
        macd, signal, hist = talib.MACD(
            data['close'],
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period
        )
        
        self.values.update({
            'macd': macd,
            'signal': signal,
            'hist': hist
        })
        
        return self.values 