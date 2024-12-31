from typing import Optional
from datetime import datetime

class Position:
    """仓位类，管理单个交易仓位"""
    
    def __init__(self, symbol: str, direction: str, entry_price: float, 
                 size: float, timestamp: datetime):
        self.symbol = symbol
        self.direction = direction  # 'long' or 'short'
        self.entry_price = entry_price
        self.size = size
        self.timestamp = timestamp
        self.exit_price: Optional[float] = None
        self.exit_timestamp: Optional[datetime] = None
        self.pnl: Optional[float] = None
        
    def calculate_pnl(self, current_price: float) -> float:
        """计算仓位盈亏"""
        if self.direction == 'long':
            self.pnl = (current_price - self.entry_price) * self.size
        else:
            self.pnl = (self.entry_price - current_price) * self.size
        return self.pnl
        
    def close(self, exit_price: float, timestamp: datetime) -> None:
        """平仓"""
        self.exit_price = exit_price
        self.exit_timestamp = timestamp
        self.calculate_pnl(exit_price)
        
    def get_value(self, current_price: float) -> float:
        """获取仓位当前市值"""
        return self.size * current_price
        
    def get_unrealized_pnl(self, current_price: float) -> float:
        """获取未实现盈亏"""
        return self.calculate_pnl(current_price)
        
    def __str__(self) -> str:
        return (f"Position({self.symbol}, {self.direction}, "
                f"entry={self.entry_price:.5f}, size={self.size:.2f})") 