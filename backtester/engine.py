from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
from strategies.base import IStrategy
from .position import Position
from .portfolio import Portfolio
from .performance import PerformanceAnalyzer
from .costs import TradingCostManager
from .visualizer import BacktestVisualizer

class BacktestEngine(ABC):
    """回测引擎基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.portfolio = Portfolio(
            initial_capital=config['risk_management'].get('initial_capital', 10000)
        )
        self.performance = PerformanceAnalyzer()
        self.positions: List[Position] = []
        self.history: List[Dict] = []
        self.cost_manager = TradingCostManager(config.get('trading_costs', {}))
        
    @abstractmethod
    def run(self, strategy: IStrategy, data: pd.DataFrame) -> Dict[str, Any]:
        """运行回测"""
        pass
        
    def process_signals(self, signals: Dict[str, Any], timestamp: datetime) -> None:
        """处理交易信号"""
        if not signals:
            return
            
        # 检查是否可以开仓
        if not self._can_open_position(signals):
            return
            
        # 计算仓位大小
        position_size = self._calculate_position_size(signals)
        if position_size <= 0:
            return
            
        # 计算交易成本
        trade_value = signals['price'] * position_size
        costs = self._calculate_trading_costs(trade_value)
        
        # 检查成本后的资金是否足够
        if not self.portfolio.has_sufficient_funds(trade_value + costs):
            return
            
        # 创建新仓位
        position = Position(
            symbol=signals['symbol'],
            direction=signals['direction'],
            entry_price=signals['price'],
            size=position_size,
            timestamp=timestamp
        )
        
        # 更新组合
        self.portfolio.add_position(position)
        self.positions.append(position)
        
        # 记录交易历史
        self._record_trade(position, 'open')
        
    def update_positions(self, current_data: pd.Series) -> None:
        """更新持仓状态"""
        for position in self.positions[:]:  # 创建副本以便在循环中移除
            if self._should_close_position(position, current_data):
                self._close_position(position, current_data)
                
    def _can_open_position(self, signals: Dict[str, Any]) -> bool:
        """检查是否可以开仓"""
        # 检查资金是否足够
        if not self.portfolio.has_sufficient_funds(signals['price'] * signals['volume']):
            return False
            
        # 检查是否达到最大持仓数
        max_positions = self.config['risk_management'].get('max_open_trades', 5)
        if len(self.positions) >= max_positions:
            return False
            
        return True
        
    def _calculate_position_size(self, signals: Dict[str, Any]) -> float:
        """计算仓位大小"""
        risk_per_trade = self.portfolio.equity * self.config['risk_management']['risk_percentage']
        return min(
            signals['volume'],
            risk_per_trade / (signals['price'] * self.config['risk_management']['stop_loss_multiplier'])
        )
        
    def _should_close_position(self, position: Position, current_data: pd.Series) -> bool:
        """检查是否应该平仓"""
        # 实现止盈止损逻辑
        if position.direction == 'long':
            stop_loss = position.entry_price * (1 - self.config['risk_management']['stop_loss_multiplier'])
            take_profit = position.entry_price * (1 + self.config['risk_management']['take_profit_multiplier'])
            return current_data['low'] <= stop_loss or current_data['high'] >= take_profit
        else:
            stop_loss = position.entry_price * (1 + self.config['risk_management']['stop_loss_multiplier'])
            take_profit = position.entry_price * (1 - self.config['risk_management']['take_profit_multiplier'])
            return current_data['high'] >= stop_loss or current_data['low'] <= take_profit
            
    def _close_position(self, position: Position, current_data: pd.Series) -> None:
        """平仓"""
        exit_price = current_data['close']
        pnl = position.calculate_pnl(exit_price)
        
        # 更新组合
        self.portfolio.remove_position(position, exit_price)
        self.positions.remove(position)
        
        # 记录交易历史
        self._record_trade(position, 'close', exit_price=exit_price, pnl=pnl)
        
    def _record_trade(self, position: Position, action: str, 
                     exit_price: Optional[float] = None, 
                     pnl: Optional[float] = None) -> None:
        """记录交易"""
        trade_record = {
            'timestamp': position.timestamp,
            'symbol': position.symbol,
            'direction': position.direction,
            'action': action,
            'price': position.entry_price if action == 'open' else exit_price,
            'size': position.size,
            'pnl': pnl if action == 'close' else None,
            'equity': self.portfolio.equity
        }
        self.history.append(trade_record) 
        
    def _calculate_trading_costs(self, trade_value: float) -> float:
        """计算交易成本"""
        return self.cost_manager.calculate_total_cost(trade_value) 
        
    def run(self, strategy: IStrategy, data: pd.DataFrame) -> Dict[str, Any]:
        # ... 现有代码 ...
        
        # 计算回测结果
        results = self.performance.calculate(
            self.history,
            self.portfolio.equity,
            data
        )
        
        # 创建可视化器
        visualizer = BacktestVisualizer(results, self.history, data)
        visualizer.generate_report()
        
        return results 