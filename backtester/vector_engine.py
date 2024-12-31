import pandas as pd
import numpy as np
from typing import Dict, Any
from .engine import BacktestEngine
from strategies.base import IStrategy

class VectorizedBacktestEngine(BacktestEngine):
    """向量化回测引擎"""
    
    def run(self, strategy: IStrategy, data: pd.DataFrame) -> Dict[str, Any]:
        """运行回测"""
        # 初始化策略
        strategy.initialize(self.config)
        
        # 遍历数据
        for timestamp, row in data.iterrows():
            # 更新策略数据
            strategy.on_data(data.loc[:timestamp])
            
            # 更新持仓
            self.update_positions(row)
            
            # 生成信号
            signals = strategy.generate_signals()
            if signals:
                self.process_signals(signals, timestamp)
                
        # 计算回测结果
        results = self.performance.calculate(
            self.history,
            self.portfolio.equity,
            data
        )
        
        return results 