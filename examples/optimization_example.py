from optimizer import GridSearchOptimizer, GeneticOptimizer
from optimizer.objectives import custom_objective
from strategies import TradingStrategy
from backtester import VectorizedBacktestEngine
import pandas as pd

# Load historical data
historical_data = pd.read_csv('data/historical_prices.csv', parse_dates=['timestamp'], index_col='timestamp')

# Create backtest engine with config
backtest_engine = VectorizedBacktestEngine(config={
    'risk_management': {
        'initial_capital': 100000,
        'risk_percentage': 0.02
    },
    'indicators': {}
})

# 定义参数空间
param_space = {
    'ma_period': list(range(10, 51, 5)),
    'bb_period': list(range(10, 51, 5)),
    'rsi_period': list(range(10, 31, 2)),
    'macd_fast': list(range(8, 21, 2)),
    'macd_slow': list(range(21, 41, 2)),
}

# 创建优化器
optimizer = GeneticOptimizer(
    strategy_class=TradingStrategy,
    param_space=param_space,
    data=historical_data,
    engine=backtest_engine,
    objective_func=custom_objective,
    population_size=50,
    generations=30
)

# 执行优化
best_params = optimizer.optimize()

# 生成可视化报告
optimizer.visualize_results()

# 使用最佳参数运行回测
strategy = TradingStrategy()
config = backtest_engine.config.copy()
config['indicators'].update(best_params)
final_results = backtest_engine.run(strategy, historical_data)

# 打印最终结果
print("\n=== Final Backtest Results ===")
for key, value in final_results.items():
    if isinstance(value, float):
        print(f"{key}: {value:.4f}")
    else:
        print(f"{key}: {value}") 