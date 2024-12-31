from typing import Dict, Any
from abc import ABC, abstractmethod

class TradingCost(ABC):
    """交易成本基类"""
    
    @abstractmethod
    def calculate(self, trade_value: float, **kwargs) -> float:
        """计算交易成本"""
        pass

class CommissionCost(TradingCost):
    """佣金成本"""
    
    def __init__(self, rate: float):
        self.rate = rate
        
    def calculate(self, trade_value: float, **kwargs) -> float:
        return trade_value * self.rate

class SpreadCost(TradingCost):
    """点差成本"""
    
    def __init__(self, spread_points: float, point_value: float):
        self.spread_points = spread_points
        self.point_value = point_value
        
    def calculate(self, trade_value: float, **kwargs) -> float:
        return self.spread_points * self.point_value

class SlippageCost(TradingCost):
    """滑点成本"""
    
    def __init__(self, slippage_pips: float):
        self.slippage_pips = slippage_pips
        
    def calculate(self, trade_value: float, **kwargs) -> float:
        return trade_value * (self.slippage_pips / 10000)

class TradingCostManager:
    """交易成本管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.costs = []
        self._initialize_costs(config)
        
    def _initialize_costs(self, config: Dict[str, Any]) -> None:
        """初始化交易成本"""
        if 'commission_rate' in config:
            self.costs.append(CommissionCost(config['commission_rate']))
            
        if 'spread_points' in config and 'point_value' in config:
            self.costs.append(SpreadCost(
                config['spread_points'],
                config['point_value']
            ))
            
        if 'slippage_pips' in config:
            self.costs.append(SlippageCost(config['slippage_pips']))
            
    def calculate_total_cost(self, trade_value: float, **kwargs) -> float:
        """计算总交易成本"""
        return sum(cost.calculate(trade_value, **kwargs) for cost in self.costs) 