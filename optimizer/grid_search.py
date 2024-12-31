from itertools import product
from typing import Dict, List, Any
import numpy as np
from .base import BaseOptimizer

class GridSearchOptimizer(BaseOptimizer):
    """网格搜索优化器"""
    
    def optimize(self) -> Dict[str, Any]:
        """执行网格搜索"""
        # 生成参数组合
        param_names = list(self.param_space.keys())
        param_values = list(self.param_space.values())
        
        # 遍历所有参数组合
        for values in product(*param_values):
            params = dict(zip(param_names, values))
            self.evaluate_params(params)
            
        return self.get_best_params() 