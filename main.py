import json
from datetime import datetime
from data_fetcher import DataFetcher
from strategy import TradingStrategy, LiveExecutor, BacktestExecutor
from optimizer import StrategyOptimizer
import pandas as pd

def optimize_strategy(data_fetcher, config):
    """
    优化策略参数
    :param data_fetcher: 数据获取器实例
    :param config: 基础配置
    :return: 优化后的配置
    """
    # 验证数据获取是否正常
    test_data = data_fetcher.get_historical_data(config)
    if test_data is None:
        print("Failed to get historical data, optimization aborted")
        return config
        
    # 创建优化器
    optimizer = StrategyOptimizer(data_fetcher)
    
    # 定义参数搜索范围
    param_ranges = {
        # 交易参数
        'trading.exit_rules.stop_loss.value': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0],
        'trading.exit_rules.take_profit.value': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
    }
    
    # 执行优化
    results = optimizer.optimize(
        param_ranges=param_ranges,
        metrics=['profit_factor', 'sharpe_ratio', 'max_drawdown', 'net_profit'],
        method='grid',
        n_jobs=-1,
        config=config
    )
    
    # 显示优化结果
    print("\nTop 10 parameter combinations (sorted by Profit Factor):")
    pd.set_option('display.float_format', '{:.4f}'.format)
    print(results.head(10).to_string())
    
    # 可视化结果
    optimizer.plot_optimization_results()
    
    # 使用profit_factor作为主要指标来选择最佳参数
    best_params = results.iloc[0]  # 已经按profit_factor排序
    best_params = {k: v for k, v in best_params.items() if not k.endswith('_score')}
    
    # 更新配置
    for key, value in best_params.items():
        if '.' in key:
            parts = key.split('.')
            current_dict = config
            for part in parts[:-1]:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]
            current_dict[parts[-1]] = value
        else:
            config[key] = value
            
    return config

def main(mode='backtest'):
    try:
        # 加载配置文件
        with open('config.json') as f:
            config = json.load(f)

        # 初始化数据获取模块
        data_fetcher = DataFetcher(
            symbol=config['symbol'],
            timeframe=str(config['timeframe'])
        )
        
        # 如果是回测模式且需要优化参数
        if mode == 'backtest' and '--optimize' in sys.argv:
            config = optimize_strategy(data_fetcher, config)
            print("\nOptimized configuration:")
            print(json.dumps(config, indent=4))

        # 初始化策略
        strategy = TradingStrategy(config)
        strategy.prepare_data(data_fetcher)

        # 根据模式选择执行器
        if mode == 'live':
            executor = LiveExecutor(config)
        else:
            executor = BacktestExecutor(strategy.data, config)

        # 执行策略
        strategy.execute(executor)

        # 生成报告
        if mode == 'backtest':
            report = executor.get_report()
            print("Backtest Results:")
            print(report)
            executor.plot_results()
        else:
            print("Live trading completed. Check logs for details.")
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # python main.py backtest --optimize  # 运行回测并优化参数
    # python main.py backtest  # 运行普通回测
    # python main.py live  # 运行实时交易
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else 'backtest'
    main(mode)
