from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime

class IStrategy(ABC):
    """策略接口基类"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        策略初始化
        Args:
            config: 策略配置参数
        """
        pass
    
    @abstractmethod
    def on_data(self, data: pd.DataFrame) -> None:
        """
        处理新数据
        Args:
            data: 市场数据
        """
        pass
    
    @abstractmethod
    def generate_signals(self) -> Dict[str, Any]:
        """
        生成交易信号
        Returns:
            包含交易信号的字典
        """
        pass
    
    @abstractmethod
    def on_trade(self, trade_info: Dict[str, Any]) -> None:
        """
        处理成交事件
        Args:
            trade_info: 成交信息
        """
        pass

class BaseStrategy(IStrategy):
    """策略基类,实现通用功能"""
    
    def __init__(self, name: str):
        self.name = name
        self.data = None  # 市场数据
        self.indicators = {}  # 技术指标
        self.positions = {}  # 持仓信息
        self.config = {}  # 策略配置
        self.logger = None  # 日志记录器
        
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化策略"""
        self.config = config
        self.setup_logger()
        self.setup_indicators()
        
    def setup_logger(self) -> None:
        """设置日志记录器"""
        from logger import TradeLogger
        self.logger = TradeLogger(f"{self.name}_strategy.log")
        
    def setup_indicators(self) -> None:
        """设置策略所需指标"""
        pass
        
    def validate_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证信号有效性
        Args:
            signals: 原始信号
        Returns:
            验证后的信号
        """
        # 基础信号验证逻辑
        if not signals:
            return {}
            
        # 检查必要字段
        required_fields = ['direction', 'price', 'volume']
        for field in required_fields:
            if field not in signals:
                self.logger.log_trade(f"Missing required field: {field}")
                return {}
                
        return signals
        
    def on_data(self, data: pd.DataFrame) -> None:
        """处理新数据"""
        self.data = data
        self.update_indicators()
        
    def update_indicators(self) -> None:
        """更新技术指标"""
        for indicator in self.indicators.values():
            indicator.update(self.data)
            
    def get_position(self, symbol: str) -> float:
        """获取品种持仓"""
        return self.positions.get(symbol, 0) 