from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Tuple
import numpy as np
import pandas as pd
from backtester.engine import BacktestEngine
from strategies.base import IStrategy
from .visualizer import OptimizationVisualizer

class BaseOptimizer(ABC):
    """优化器基类"""
    
    def __init__(self, strategy_class: type, 
                 param_space: Dict[str, List[Any]],
                 data: pd.DataFrame,
                 engine: BacktestEngine,
                 objective_func: Callable[[Dict[str, Any]], float]):
        self.strategy_class = strategy_class
        self.param_space = param_space
        self.data = data
        self.engine = engine
        self.objective_func = objective_func
        self.results: List[Dict[str, Any]] = []
        
    @abstractmethod
    def optimize(self) -> Dict[str, Any]:
        """执行优化"""
        pass
        
    def evaluate_params(self, params: Dict[str, Any]) -> float:
        """评估参数组合"""
        # 创建策略实例
        strategy = self.strategy_class()
        
        # 更新策略配置
        config = self.engine.config.copy()
        config['indicators'].update(params)
        
        # 运行回测
        results = self.engine.run(strategy, self.data)
        
        # 记录结果
        self.results.append({
            'params': params,
            'metrics': results,
            'score': self.objective_func(results)
        })
        
        return self.objective_func(results)
        
    def get_best_params(self) -> Dict[str, Any]:
        """获取最优参数"""
        if not self.results:
            return {}
            
        best_result = max(self.results, key=lambda x: x['score'])
        return best_result['params'] 
        
    def visualize_results(self) -> None:
        """可视化优化结果"""
        if not self.results:
            print("No optimization results to visualize")
            return
        
        visualizer = OptimizationVisualizer(self.results)
        visualizer.generate_report() 