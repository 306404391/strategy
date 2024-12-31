import pandas as pd
import numpy as np
from typing import Dict, Any, List

class PerformanceAnalyzer:
    """性能分析器"""
    
    def calculate(self, trade_history: List[Dict], 
                 final_equity: float,
                 price_data: pd.DataFrame) -> Dict[str, Any]:
        """计算回测性能指标"""
        if not trade_history:
            return {}
            
        # 创建交易记录DataFrame
        trades_df = pd.DataFrame(trade_history)
        
        # 计算基础指标
        total_trades = len(trades_df[trades_df['action'] == 'close'])
        winning_trades = len(trades_df[(trades_df['action'] == 'close') & (trades_df['pnl'] > 0)])
        losing_trades = len(trades_df[(trades_df['action'] == 'close') & (trades_df['pnl'] < 0)])
        
        # 计算盈利指标
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        net_profit = gross_profit - gross_loss
        
        # 计算其他指标
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
        # 计算回撤
        equity_curve = trades_df['equity'].fillna(method='ffill')
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        # 计算夏普比率
        returns = equity_curve.pct_change().dropna()
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        
        # 添加新指标
        sortino_ratio = self._calculate_sortino_ratio(returns)
        calmar_ratio = self._calculate_calmar_ratio(returns, max_drawdown)
        
        # 计算交易统计
        avg_trade_duration = self._calculate_avg_trade_duration(trades_df)
        profit_factor = self._calculate_profit_factor(trades_df)
        
        results = {
            'Total Trades': total_trades,
            'Winning Trades': winning_trades,
            'Losing Trades': losing_trades,
            'Win Rate': win_rate,
            'Gross Profit': gross_profit,
            'Gross Loss': gross_loss,
            'Net Profit': net_profit,
            'Profit Factor': profit_factor,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio,
            'Final Equity': final_equity,
            'Sortino Ratio': sortino_ratio,
            'Calmar Ratio': calmar_ratio,
            'Average Trade Duration': avg_trade_duration,
            'Profit Factor': profit_factor
        }
        
        return results
        
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """计算最大回撤"""
        rolling_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - rolling_max) / rolling_max
        return abs(drawdowns.min())
        
    def _calculate_sharpe_ratio(self, returns: pd.Series, 
                              risk_free_rate: float = 0.0, 
                              periods_per_year: int = 252) -> float:
        """计算夏普比率"""
        excess_returns = returns - risk_free_rate / periods_per_year
        return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std() 
        
    def _calculate_sortino_ratio(self, returns: pd.Series, 
                               risk_free_rate: float = 0.0,
                               periods_per_year: int = 252) -> float:
        """计算索提诺比率"""
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.sqrt(np.mean(downside_returns ** 2))
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std
        
    def _calculate_calmar_ratio(self, returns: pd.Series, 
                              max_drawdown: float,
                              periods_per_year: int = 252) -> float:
        """计算卡玛比率"""
        annual_return = returns.mean() * periods_per_year
        return annual_return / max_drawdown
        
    def _calculate_avg_trade_duration(self, trades_df: pd.DataFrame) -> float:
        """计算平均交易持续时间"""
        trade_durations = []
        for _, trade in trades_df.iterrows():
            if trade['action'] == 'close':
                duration = (trade['timestamp'] - 
                          trades_df[trades_df['action'] == 'open'].iloc[0]['timestamp'])
                trade_durations.append(duration.total_seconds() / 3600)  # 转换为小时
                
        return np.mean(trade_durations)
        
    def _calculate_profit_factor(self, trades_df: pd.DataFrame) -> float:
        """计算利润因子"""
        profits = trades_df[trades_df['pnl'] > 0]['pnl']
        losses = trades_df[trades_df['pnl'] < 0]['pnl']
        return np.sum(profits) / np.sum(abs(losses)) 