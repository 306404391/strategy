import logging
import pandas as pd
from datetime import datetime

class TradeLogger:
    def __init__(self, log_file='trading_log.log'):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        self.trades = []

    def log_trade(self, trade_details):
        logging.info(trade_details)
        self.trades.append(trade_details)

    def generate_performance_report(self):
        if not self.trades:
            return None

        df = pd.DataFrame(self.trades)
        total_profit = df[df['profit'] > 0]['profit'].sum()
        total_loss = abs(df[df['profit'] < 0]['profit'].sum())
        win_rate = len(df[df['profit'] > 0]) / len(df) * 100
        risk_reward_ratio = total_profit / total_loss if total_loss != 0 else 0
        max_drawdown = self.calculate_max_drawdown(df['equity'])

        report = {
            'Total Profit': total_profit,
            'Total Loss': total_loss,
            'Win Rate (%)': win_rate,
            'Risk Reward Ratio': risk_reward_ratio,
            'Max Drawdown': max_drawdown
        }
        return report

    def calculate_max_drawdown(self, equity_series):
        cumulative_max = equity_series.cummax()
        drawdown = (equity_series - cumulative_max) / cumulative_max
        return drawdown.min()
