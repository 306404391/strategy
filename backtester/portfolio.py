from typing import Dict, List, Optional
from datetime import datetime
from .position import Position

class Portfolio:
    """投资组合类，管理所有仓位和资金"""
    
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.equity = initial_capital
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        self.trade_history: List[Dict] = []
        
    def add_position(self, position: Position) -> None:
        """添加新仓位"""
        # 计算所需保证金
        margin = position.get_value(position.entry_price)
        
        # 检查资金是否足够
        if not self.has_sufficient_funds(margin):
            raise ValueError("Insufficient funds to open position")
            
        # 更新现金和权益
        self.cash -= margin
        self.positions[position.symbol] = position
        self.update_equity()
        
        # 记录交易
        self._record_trade(position, 'open')
        
    def remove_position(self, position: Position, exit_price: float) -> None:
        """移除仓位"""
        if position.symbol not in self.positions:
            return
            
        # 平仓
        position.close(exit_price, datetime.now())
        
        # 更新现金和权益
        self.cash += position.get_value(exit_price)
        del self.positions[position.symbol]
        self.closed_positions.append(position)
        self.update_equity()
        
        # 记录交易
        self._record_trade(position, 'close')
        
    def update_equity(self) -> None:
        """更新组合权益"""
        unrealized_pnl = sum(
            pos.get_unrealized_pnl(pos.entry_price)  # 这里应该使用最新价格，简化处理
            for pos in self.positions.values()
        )
        self.equity = self.cash + unrealized_pnl
        
    def has_sufficient_funds(self, required_margin: float) -> bool:
        """检查是否有足够资金"""
        return self.cash >= required_margin
        
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取指定品种的仓位"""
        return self.positions.get(symbol)
        
    def get_total_value(self) -> float:
        """获取组合总价值"""
        return self.equity
        
    def get_position_value(self, symbol: str) -> float:
        """获取指定仓位的市值"""
        position = self.get_position(symbol)
        if not position:
            return 0.0
        return position.get_value(position.entry_price)  # 这里应该使用最新价格
        
    def _record_trade(self, position: Position, action: str) -> None:
        """记录交易"""
        trade = {
            'timestamp': position.timestamp,
            'symbol': position.symbol,
            'action': action,
            'direction': position.direction,
            'price': position.entry_price if action == 'open' else position.exit_price,
            'size': position.size,
            'pnl': position.pnl if action == 'close' else None,
            'cash': self.cash,
            'equity': self.equity
        }
        self.trade_history.append(trade) 