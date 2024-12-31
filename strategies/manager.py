from typing import Dict, Type, Optional
from .base import IStrategy

class StrategyManager:
    """策略管理器"""
    
    def __init__(self):
        self._strategies: Dict[str, IStrategy] = {}
        self._strategy_classes: Dict[str, Type[IStrategy]] = {}
        
    def register_strategy(self, name: str, strategy_class: Type[IStrategy]) -> None:
        """
        注册策略类
        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        self._strategy_classes[name] = strategy_class
        
    def create_strategy(self, name: str, config: Dict) -> Optional[IStrategy]:
        """
        创建策略实例
        Args:
            name: 策略名称
            config: 策略配置
        Returns:
            策略实例
        """
        if name not in self._strategy_classes:
            raise ValueError(f"Strategy {name} not registered")
            
        strategy = self._strategy_classes[name](name)
        strategy.initialize(config)
        self._strategies[name] = strategy
        return strategy
        
    def get_strategy(self, name: str) -> Optional[IStrategy]:
        """获取策略实例"""
        return self._strategies.get(name)
        
    def remove_strategy(self, name: str) -> None:
        """移除策略"""
        if name in self._strategies:
            del self._strategies[name] 