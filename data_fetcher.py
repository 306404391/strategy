"""
数据获取模块，负责从MT5平台获取历史和实时市场数据
"""

import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd

class DataFetcher:
    """数据获取器，封装MT5数据获取功能"""
    
    def __init__(self, symbol="EURUSD", timeframe="H1"):
        """
        初始化数据获取器
        :param symbol: 交易品种，默认为EURUSD
        :param timeframe: 时间框架字符串，默认为"H1"
        """
        self.symbol = symbol
        self.timeframe = self._convert_timeframe(timeframe)
        
        # 初始化MT5连接
        if not mt5.initialize():
            print("Failed to initialize MT5 connection, error code:", mt5.last_error())
            raise ConnectionError("Failed to connect to MT5")
            
        # 检查交易品种是否可用
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"Symbol {self.symbol} is not available")
            raise ValueError(f"Invalid symbol: {self.symbol}")

    def _convert_timeframe(self, timeframe_str):
        """
        将时间框架字符串转换为MT5常量
        :param timeframe_str: 时间框架字符串（如"H1"）
        :return: MT5时间框架常量
        """
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }
        
        if timeframe_str not in timeframe_map:
            print(f"Warning: Invalid timeframe {timeframe_str}, using H1 instead")
            return mt5.TIMEFRAME_H1
        
        return timeframe_map[timeframe_str]

    def get_historical_data(self, config):
        """获取历史数据"""
        try:
            # 确保MT5已初始化
            if not mt5.initialize():
                print("Failed to initialize MT5")
                mt5.shutdown()
                return None

            # 使用已转换的时间框架
            timeframe = self.timeframe  # 使用初始化时已转换的时间框架
            
            if config['data_settings']['history_type'] == 'by_date':
                # 按日期范围获取数据
                from_date = pd.to_datetime(config['data_settings']['start_date'])
                rates = mt5.copy_rates_from(
                    self.symbol,
                    timeframe,
                    from_date,
                    config['data_settings'].get('num_bars', 100000)
                )
            else:
                # 按K线数量获取数据
                rates = mt5.copy_rates_from_pos(
                    self.symbol,
                    timeframe,
                    0,
                    config['data_settings'].get('num_bars', 100000)
                )

            if rates is None or len(rates) == 0:
                print(f"Failed to get historical data from MT5 for {self.symbol}")
                return None

            # 转换为DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            print(f"Retrieved {len(df)} bars of historical data")
            print(f"Data range: from {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
            
            return df

        except Exception as e:
            print(f"Failed to get historical data from MT5: {str(e)}")
            return None

    def get_realtime_data(self):
        """
        获取实时市场数据
        :return: 包含实时数据的字典
        """
        # 获取最新tick数据
        tick = mt5.symbol_info_tick(self.symbol)
        return {
            'time': datetime.now(),  # 当前时间
            'bid': tick.bid,  # 买价
            'ask': tick.ask,  # 卖价
            'volume': tick.volume  # 成交量
        }
