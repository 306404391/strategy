import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
from datetime import datetime

class BacktestVisualizer:
    """回测结果可视化"""
    
    def __init__(self, results: Dict[str, Any], trade_history: List[Dict], 
                 price_data: pd.DataFrame):
        self.results = results
        self.trades_df = pd.DataFrame(trade_history)
        self.price_data = price_data
        self._prepare_data()
        
    def _prepare_data(self) -> None:
        """准备可视化数据"""
        # 创建权益曲线
        self.equity_curve = self.trades_df['equity'].fillna(method='ffill')
        
        # 计算回撤
        rolling_max = self.equity_curve.expanding().max()
        self.drawdown = (self.equity_curve - rolling_max) / rolling_max * 100
        
        # 计算收益率
        self.returns = self.equity_curve.pct_change()
        
    def plot_equity_curve(self, figsize=(12, 6)) -> None:
        """绘制权益曲线"""
        plt.figure(figsize=figsize)
        plt.plot(self.equity_curve.index, self.equity_curve.values, label='Equity')
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Equity')
        plt.grid(True)
        plt.legend()
        plt.show()
        
    def plot_drawdown(self, figsize=(12, 6)) -> None:
        """绘制回撤曲线"""
        plt.figure(figsize=figsize)
        plt.fill_between(self.drawdown.index, self.drawdown.values, 0, 
                        color='red', alpha=0.3)
        plt.title('Drawdown')
        plt.xlabel('Date')
        plt.ylabel('Drawdown (%)')
        plt.grid(True)
        plt.show()
        
    def plot_monthly_returns(self, figsize=(12, 6)) -> None:
        """绘制月度收益分布"""
        monthly_returns = self.returns.resample('M').sum() * 100
        
        plt.figure(figsize=figsize)
        monthly_returns.plot(kind='bar')
        plt.title('Monthly Returns')
        plt.xlabel('Month')
        plt.ylabel('Return (%)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.show()
        
    def plot_trade_analysis(self, figsize=(15, 10)) -> None:
        """绘制交易分析图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 盈亏分布
        profits = self.trades_df[self.trades_df['pnl'] > 0]['pnl']
        losses = self.trades_df[self.trades_df['pnl'] < 0]['pnl']
        
        sns.histplot(profits, ax=ax1, color='green', alpha=0.5, label='Profits')
        sns.histplot(losses, ax=ax1, color='red', alpha=0.5, label='Losses')
        ax1.set_title('Profit/Loss Distribution')
        ax1.legend()
        
        # 交易持续时间分布
        trade_durations = []
        for _, trade in self.trades_df.iterrows():
            if trade['action'] == 'close':
                duration = (trade['timestamp'] - 
                          self.trades_df[self.trades_df['action'] == 'open'].iloc[0]['timestamp'])
                trade_durations.append(duration.total_seconds() / 3600)  # 转换为小时
                
        sns.histplot(trade_durations, ax=ax2)
        ax2.set_title('Trade Duration Distribution (hours)')
        
        # 累计盈亏曲线
        cumulative_pnl = self.trades_df[self.trades_df['pnl'].notna()]['pnl'].cumsum()
        ax3.plot(cumulative_pnl.index, cumulative_pnl.values)
        ax3.set_title('Cumulative P&L')
        ax3.grid(True)
        
        # 每月交易次数
        monthly_trades = self.trades_df.resample('M', on='timestamp').size()
        ax4.bar(monthly_trades.index, monthly_trades.values)
        ax4.set_title('Monthly Trade Count')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
        
    def plot_trade_locations(self, figsize=(12, 6)) -> None:
        """在价格图上标注交易位置"""
        plt.figure(figsize=figsize)
        
        # 绘制价格
        plt.plot(self.price_data.index, self.price_data['close'], 
                color='gray', alpha=0.5)
        
        # 标注交易点
        for _, trade in self.trades_df.iterrows():
            if trade['action'] == 'open':
                color = 'g' if trade['direction'] == 'long' else 'r'
                marker = '^' if trade['direction'] == 'long' else 'v'
                plt.scatter(trade['timestamp'], trade['price'], 
                          color=color, marker=marker, s=100)
                
        plt.title('Trade Locations')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.grid(True)
        plt.show()
        
    def generate_report(self) -> None:
        """生成完整的回测报告"""
        self.plot_equity_curve()
        self.plot_drawdown()
        self.plot_monthly_returns()
        self.plot_trade_analysis()
        self.plot_trade_locations()
        
        # 打印统计指标
        print("\n=== Backtest Results ===")
        for key, value in self.results.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}") 