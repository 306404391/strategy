"""
交易执行模块，负责通过MT5 API执行交易订单
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

class TradeExecutor:
    """交易执行器，封装MT5交易执行功能"""
    
    def __init__(self, symbol="EURUSD", magic_number=234000):
        """
        初始化交易执行器
        :param symbol: 交易品种，默认为EURUSD
        :param magic_number: 订单标识符，用于区分不同策略的订单
        """
        self.symbol = symbol
        self.magic_number = magic_number
        mt5.initialize()  # 初始化MT5连接

    def place_order(self, order_type, price, volume, sl, tp):
        """
        下单操作
        :param order_type: 订单类型，'buy'或'sell'
        :param price: 订单价格
        :param volume: 交易量
        :param sl: 止损价格
        :param tp: 止盈价格
        :return: 订单执行结果
        """
        # 转换订单类型
        order_type = mt5.ORDER_TYPE_BUY if order_type == 'buy' else mt5.ORDER_TYPE_SELL
        # 构建订单请求
        request = {
            "action": mt5.TRADE_ACTION_DEAL,  # 立即执行订单
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,  # 止损
            "tp": tp,  # 止盈
            "deviation": 20,  # 允许的最大价格偏差
            "magic": self.magic_number,  # 订单标识符
            "comment": "Python script open",  # 订单注释
            "type_time": mt5.ORDER_TIME_GTC,  # 订单有效期直到取消
            "type_filling": mt5.ORDER_FILLING_IOC,  # 立即成交否则取消
        }
        # 发送订单请求
        result = mt5.order_send(request)
        return result

    def close_order(self, position, price):
        """
        平仓操作
        :param position: 要平仓的持仓
        :param price: 平仓价格
        :return: 平仓执行结果
        """
        # 确定平仓订单类型
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        # 构建平仓请求
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": position.ticket,  # 要平仓的持仓ID
            "price": price,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": "Python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # 发送平仓请求
        result = mt5.order_send(request)
        return result

    def get_open_positions(self):
        """
        获取当前持仓
        :return: 包含当前持仓的DataFrame
        """
        positions = mt5.positions_get(symbol=self.symbol)
        return pd.DataFrame(positions)

    def manage_trades(self, data):
        """
        管理交易，根据信号执行买卖操作
        :param data: 包含交易信号和指标数据的DataFrame
        """
        for index, row in data.iterrows():
            if row['long_signal']:
                # 计算多头止损和止盈
                sl = row['close'] - 1.5 * row['ATR']
                tp = row['close'] + 2 * row['ATR']
                self.place_order('buy', row['close'], 0.1, sl, tp)
            elif row['short_signal']:
                # 计算空头止损和止盈
                sl = row['close'] + 1.5 * row['ATR']
                tp = row['close'] - 2 * row['ATR']
                self.place_order('sell', row['close'], 0.1, sl, tp)
