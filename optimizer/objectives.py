from typing import Dict, Any

def sharpe_ratio_objective(results: Dict[str, Any]) -> float:
    """夏普比率优化目标"""
    return results.get('Sharpe Ratio', float('-inf'))

def sortino_ratio_objective(results: Dict[str, Any]) -> float:
    """索提诺比率优化目标"""
    return results.get('Sortino Ratio', float('-inf'))

def custom_objective(results: Dict[str, Any]) -> float:
    """自定义优化目标"""
    sharpe = results.get('Sharpe Ratio', 0)
    drawdown = results.get('Max Drawdown', 100)
    win_rate = results.get('Win Rate', 0)
    
    return (sharpe * 0.4 + (1 - drawdown/100) * 0.3 + win_rate * 0.3) 