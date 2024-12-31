"""
回测模块，负责策略的历史回测和性能评估
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class Backtester:
    """回测器，用于执行策略回测和生成性能报告"""
    
    def __init__(self, config, initial_balance=10000):
        """
        初始化回测器
        :param config: 配置字典
        :param initial_balance: 初始资金
        """
        self.config = config
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity_curve = []
        self.trades = []
        self.commission_per_lot = config['risk_management']['commission_per_lot']
        self.allow_consecutive_trades = config['trading'].get('allow_consecutive_trades', False)
        self.last_trade_type = None  # 记录上一笔交易的方向
        
    def calculate_position_size(self, price, atr):
        """
        计算仓位大小
        :param price: 当前价格
        :param atr: 当前ATR值
        :return: 交易手数
        """
        sizing_config = self.config['risk_management']['position_sizing']
        
        if sizing_config['type'] == 'fixed':
            return sizing_config['fixed_volume']
        else:  # risk_based
            risk_amount = self.balance * self.config['risk_management']['risk_percentage']
            stop_loss_pips = atr * self.config['risk_management']['stop_loss_multiplier']
            pip_value = 10  # 假设1手=10美元/点，根据实际情况调整
            return round(risk_amount / (stop_loss_pips * pip_value), 2)

    def calculate_exit_prices(self, entry_price, atr, position_type):
        """
        计算出场价格
        :param entry_price: 入场价格
        :param atr: 当前ATR值
        :param position_type: 持仓类型 'long' 或 'short'
        :return: (stop_loss, take_profit)
        """
        sl_config = self.config['trading']['exit_rules']['stop_loss']
        tp_config = self.config['trading']['exit_rules']['take_profit']
        
        if position_type == 'long':
            if sl_config['type'] == 'fixed':
                stop_loss = entry_price - (atr * sl_config['value'])
            # 可以添加其他止损类型的计算逻辑
            
            if tp_config['type'] == 'fixed':
                take_profit = entry_price + (atr * tp_config['value'])
            # 可以添加其他止盈类型的计算逻辑
        else:  # short
            if sl_config['type'] == 'fixed':
                stop_loss = entry_price + (atr * sl_config['value'])
            
            if tp_config['type'] == 'fixed':
                take_profit = entry_price - (atr * tp_config['value'])
                
        return stop_loss, take_profit

    def calculate_commission(self, volume):
        """
        计算手续费
        :param volume: 交易手数
        :return: 手续费金额
        """
        return volume * self.commission_per_lot

    def run_backtest(self, data):
        """
        执行回测
        :param data: 包含交易信号和价格数据的DataFrame
        """
        position = None
        entry_price = 0
        volume = 0
        stop_loss = 0
        take_profit = 0
        
        for index, row in data.iterrows():
            # 更新权益曲线
            if position:
                unrealized_pnl = 0
                if position == 'long':
                    unrealized_pnl = (row['close'] - entry_price) * volume * 100000
                else:  # short
                    unrealized_pnl = (entry_price - row['close']) * volume * 100000
                current_equity = self.balance + unrealized_pnl
                self.equity_curve.append(current_equity)
                
                # 检查是否触及止损或止盈
                if position == 'long':
                    if row['low'] <= stop_loss or row['high'] >= take_profit:
                        exit_price = stop_loss if row['low'] <= stop_loss else take_profit
                        pnl = (exit_price - entry_price) * volume * 100000
                        commission = self.calculate_commission(volume)
                        self.balance += pnl - commission
                        self.last_trade_type = 'long'  # 记录这笔交易的方向
                        position = None
                        
                        self.trades.append({
                            'type': 'long',
                            'entry': entry_price,
                            'exit': exit_price,
                            'volume': volume,
                            'pnl': pnl,
                            'commission': commission,
                            'time': index  # 记录交易时间
                        })
                else:  # short
                    if row['high'] >= stop_loss or row['low'] <= take_profit:
                        exit_price = stop_loss if row['high'] >= stop_loss else take_profit
                        pnl = (entry_price - exit_price) * volume * 100000
                        commission = self.calculate_commission(volume)
                        self.balance += pnl - commission
                        self.last_trade_type = 'short'  # 记录这笔交易的方向
                        position = None
                        
                        self.trades.append({
                            'type': 'short',
                            'entry': entry_price,
                            'exit': exit_price,
                            'volume': volume,
                            'pnl': pnl,
                            'commission': commission,
                            'time': index  # 记录交易时间
                        })

            # 处理新的交易信号
            if not position:  # 只在没有持仓时开新仓
                can_open_long = row['long_signal'] and (
                    self.allow_consecutive_trades or  # 如果允许连续交易
                    self.last_trade_type != 'long'    # 或者上一笔不是做多
                )
                can_open_short = row['short_signal'] and (
                    self.allow_consecutive_trades or  # 如果允许连续交易
                    self.last_trade_type != 'short'   # 或者上一笔不是做空
                )
                
                if can_open_long:
                    volume = self.calculate_position_size(row['close'], row['ATR'])
                    entry_price = row['close']
                    stop_loss, take_profit = self.calculate_exit_prices(entry_price, row['ATR'], 'long')
                    position = 'long'
                    
                elif can_open_short:
                    volume = self.calculate_position_size(row['close'], row['ATR'])
                    entry_price = row['close']
                    stop_loss, take_profit = self.calculate_exit_prices(entry_price, row['ATR'], 'short')
                    position = 'short'

    def generate_report(self):
        """
        生成回测报告
        :return: 包含回测结果的字典
        """
        if not self.trades:
            return None

        df = pd.DataFrame(self.trades)
        total_profit = df['pnl'].sum()
        total_commission = df['commission'].sum()
        net_profit = total_profit - total_commission
        win_rate = len(df[df['pnl'] > 0]) / len(df) * 100
        max_drawdown = self.calculate_max_drawdown()

        report = {
            'Initial Balance': self.initial_balance,
            'Final Balance': self.balance,
            'Net Profit': net_profit,
            'Total Commission': total_commission,
            'Win Rate (%)': win_rate,
            'Max Drawdown (%)': max_drawdown * 100,
            'Number of Trades': len(self.trades),
            'Average Profit per Trade': net_profit / len(self.trades) if len(self.trades) > 0 else 0,
            'Profit Factor': abs(df[df['pnl'] > 0]['pnl'].sum() / df[df['pnl'] < 0]['pnl'].sum()) if len(df[df['pnl'] < 0]) > 0 else float('inf')
        }
        return report

    def calculate_max_drawdown(self):
        """
        计算最大回撤
        :return: 最大回撤百分比
        """
        cumulative_max = pd.Series(self.equity_curve).cummax()  # 计算累计最大值
        drawdown = (pd.Series(self.equity_curve) - cumulative_max) / cumulative_max
        return drawdown.min()

    def plot_equity_curve(self):
        """绘制权益曲线图"""
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve)
        plt.title('Equity Curve')
        plt.xlabel('Time')
        plt.ylabel('Balance')
        plt.grid(True)
        plt.show()
