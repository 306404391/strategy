"""
技术指标计算模块，包含多种波动性指标的计算方法
"""

import pandas as pd
import talib

class Indicators:
    """技术指标计算器，封装多种波动性指标的计算方法"""
    
    def __init__(self, data):
        """
        初始化指标计算器
        :param data: 包含市场数据的DataFrame
        """
        self.data = data

    def calculate_atr(self, window=14):
        """
        计算平均真实波动幅度（ATR）
        :param window: 计算窗口，默认为14
        """
        self.data['ATR'] = talib.ATR(
            self.data['high'].values,
            self.data['low'].values,
            self.data['close'].values,
            timeperiod=window
        )

    def calculate_bollinger_bands(self, window=20, window_dev=2):
        """
        计算布林带指标
        :param window: 计算窗口，默认为20
        :param window_dev: 标准差倍数，默认为2
        """
        upper, middle, lower = talib.BBANDS(
            self.data['close'].values,
            timeperiod=window,
            nbdevup=window_dev,
            nbdevdn=window_dev
        )
        self.data['BB_upper'] = upper
        self.data['BB_middle'] = middle
        self.data['BB_lower'] = lower

    def calculate_donchian_channels(self, window=20):
        """
        计算唐奇安通道
        :param window: 计算窗口，默认为20
        """
        self.data['DC_upper'] = self.data['high'].rolling(window=window).max()
        self.data['DC_lower'] = self.data['low'].rolling(window=window).min()

    def calculate_keltner_channels(self, ema_window=20, atr_multiplier=1.5):
        """
        计算凯尔特纳通道
        :param ema_window: EMA计算窗口，默认为20
        :param atr_multiplier: ATR倍数，默认为1.5
        """
        self.data['KC_middle'] = talib.EMA(self.data['close'].values, timeperiod=ema_window)
        self.data['KC_upper'] = self.data['KC_middle'] + (atr_multiplier * self.data['ATR'])
        self.data['KC_lower'] = self.data['KC_middle'] - (atr_multiplier * self.data['ATR'])

    def calculate_chaikin_volatility(self, window=10):
        """
        计算乔金波动率
        :param window: 计算窗口，默认为10
        """
        self.data['Volatility_Chaikin'] = (
            self.data['high'].rolling(window=window).std() / 
            self.data['low'].rolling(window=window).std()
        )

    def calculate_rvi(self, window=14, signal_window=4):
        """
        计算相对波动指数（RVI）
        :param window: RVI计算窗口，默认为14
        :param signal_window: 信号线计算窗口，默认为4
        """
        self.data['RVI'] = talib.RSI(self.data['close'].values, timeperiod=window)
        self.data['RVI_signal'] = talib.MA(self.data['RVI'].values, timeperiod=signal_window)

    def calculate_all_indicators(self):
        """计算所有技术指标"""
        self.calculate_atr()
        self.calculate_bollinger_bands()
        self.calculate_donchian_channels()
        self.calculate_keltner_channels()
        self.calculate_chaikin_volatility()
        self.calculate_rvi()
