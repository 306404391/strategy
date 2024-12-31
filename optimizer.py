import itertools
import multiprocessing as mp
import random
from typing import Dict, List, Callable, Union, Tuple
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from backtester import Backtester
from strategy import TradingStrategy
from indicators import Indicators
from signal_generator import SignalGenerator
from datetime import datetime

class StrategyOptimizer:
    """策略参数优化器"""
    
    def __init__(self, data_fetcher, initial_capital: float = 10000):
        """
        初始化优化器
        :param data_fetcher: DataFetcher实例
        :param initial_capital: 初始资金
        """
        self.data_fetcher = data_fetcher
        self.initial_capital = initial_capital
        self.optimization_results = []
        
    def define_parameters(self, param_ranges: Dict[str, Union[List, range]]) -> List[Dict]:
        """
        定义参数搜索空间
        :param param_ranges: 参数范围字典，如:
            {
                'atr_window': range(10, 30, 2),
                'rvi_window': [10, 14, 20, 25],
                'risk_percentage': [0.01, 0.02, 0.03]
            }
        :return: 所有参数组合的列表
        """
        # 生成所有可能的参数组合
        keys = param_ranges.keys()
        values = param_ranges.values()
        combinations = list(itertools.product(*values))
        
        # 转换为字典列表
        param_combinations = []
        for combo in combinations:
            param_dict = dict(zip(keys, combo))
            param_combinations.append(param_dict)
            
        return param_combinations
        
    def _evaluate_parameters(self, params: Dict, 
                           metric: str = 'sharpe_ratio',
                           config: Dict = None) -> Tuple[Dict, float]:
        """
        评估单个参数组合
        :param params: 参数字典
        :param metric: 评估指标
        :param config: 基础配置
        :return: (参数字典, 评估分数)
        """
        try:
            # 更新配置
            if config is None:
                config = {}
            
            test_config = config.copy()
            
            # 更新配置中的参数
            for key, value in params.items():
                if '.' in key:
                    parts = key.split('.')
                    current_dict = test_config
                    
                    for part in parts[:-1]:
                        if part not in current_dict:
                            current_dict[part] = {}
                        current_dict = current_dict[part]
                    
                    current_dict[parts[-1]] = value
                else:
                    test_config[key] = value
            
            # 初始化策略并生成信号
            strategy = TradingStrategy(test_config)
            data = self.data_fetcher.get_historical_data(test_config)
            
            if data is None:
                print("Failed to get historical data, skipping this parameter combination")
                return params, float('-inf')  # 返回一个很差的分数
            
            strategy.data = data
            strategy.indicators = Indicators(data)
            strategy.indicators.calculate_all_indicators()
            strategy.signals = SignalGenerator(data)
            strategy.signals.generate_all_signals()
            
            # 执行回测
            backtester = Backtester(test_config, self.initial_capital)
            backtester.run_backtest(strategy.data)
            results = backtester.generate_report()
            
            # 计算评估分数
            if metric == 'sharpe_ratio':
                score = self._calculate_sharpe_ratio(results)
            elif metric == 'profit_factor':
                score = results['Profit Factor']
            elif metric == 'max_drawdown':
                score = -results['Max Drawdown (%)']
            elif metric == 'net_profit':
                score = results['Net Profit']
            else:
                raise ValueError(f"Unsupported metric: {metric}")
            
            return params, score
            
        except Exception as e:
            print(f"Error evaluating parameters: {str(e)}")
            return params, float('-inf')  # 返回一个很差的分数
        
    def _calculate_sharpe_ratio(self, results: Dict) -> float:
        """
        计算夏普比率
        :param results: 回测结果
        :return: 夏普比率
        """
        returns = pd.Series(results['Daily Returns'])
        risk_free_rate = 0.02  # 年化无风险利率
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1
        
        excess_returns = returns - daily_rf
        if excess_returns.std() == 0:
            return 0
            
        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return sharpe
        
    def optimize(self, param_ranges: Dict[str, Union[List, range]],
                metrics: List[str] = ['profit_factor', 'sharpe_ratio', 'max_drawdown', 'net_profit'],
                method: str = 'grid',
                n_iterations: int = None,
                n_jobs: int = -1,
                config: Dict = None) -> pd.DataFrame:
        """
        执行参数优化
        :param param_ranges: 参数范围字典
        :param metrics: 评估指标列表
        :param method: 优化方法 ('grid' 或 'random')
        :param n_iterations: 随机搜索的迭代次数
        :param n_jobs: 并行进程数，-1表示使用所有可用核心
        :param config: 基础配置
        :return: 优化结果DataFrame
        """
        if method == 'grid':
            param_combinations = self.define_parameters(param_ranges)
        elif method == 'random':
            if n_iterations is None:
                raise ValueError("n_iterations must be specified for random search")
            param_combinations = self._generate_random_combinations(param_ranges, n_iterations)
        else:
            raise ValueError(f"Unsupported optimization method: {method}")
            
        # 设置并行进程数
        if n_jobs == -1:
            n_jobs = mp.cpu_count()
        
        # 创建进程池
        with mp.Pool(n_jobs) as pool:
            # 使用partial固定其他参数
            from functools import partial
            eval_func = partial(self._evaluate_parameters_multi_metric, 
                              metrics=metrics,
                              config=config)
            
            # 执行并行优化
            results = list(tqdm(
                pool.imap(eval_func, param_combinations),
                total=len(param_combinations),
                desc="Optimizing parameters"
            ))
            
        # 整理结果
        results_df = pd.DataFrame([
            {**params, **scores}
            for params, scores in results
        ])
        
        # 重命名列
        column_mapping = {
            'trading.exit_rules.stop_loss.value': 'Stop Loss',
            'trading.exit_rules.take_profit.value': 'Take Profit'
        }
        results_df = results_df.rename(columns=column_mapping)
        
        # 按profit_factor_score降序排序，去除无效结果
        results_df = results_df[results_df['profit_factor_score'] > 0]
        self.optimization_results = results_df.sort_values('profit_factor_score', ascending=False).reset_index(drop=True)
        
        # 保存到Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f'optimization_results_{timestamp}.xlsx'
        self.optimization_results.to_excel(excel_path, index=True)  # 添加索引列
        print(f"\nResults saved to {excel_path}")
        
        return self.optimization_results
        
    def _generate_random_combinations(self, param_ranges: Dict[str, Union[List, range]], 
                                    n_iterations: int) -> List[Dict]:
        """
        生成随机参数组合
        :param param_ranges: 参数范围字典
        :param n_iterations: 迭代次数
        :return: 随机参数组合列表
        """
        combinations = []
        for _ in range(n_iterations):
            params = {}
            for key, value_range in param_ranges.items():
                if isinstance(value_range, (list, tuple)):
                    params[key] = random.choice(value_range)
                elif isinstance(value_range, range):
                    params[key] = random.choice(list(value_range))
                else:
                    raise ValueError(f"Unsupported parameter range type for {key}")
            combinations.append(params)
        return combinations
        
    def plot_optimization_results(self, top_n: int = 10):
        """可视化优化结果"""
        if len(self.optimization_results) == 0:
            raise ValueError("No optimization results available. Run optimize() first.")
            
        results = self.optimization_results
        param_cols = [col for col in results.columns if not col.endswith('_score')]
        score_cols = [col for col in results.columns if col.endswith('_score')]
        n_params = len(param_cols)
        
        # 1. 为每个评估指标绘制散点图
        for score_col in score_cols:
            fig, axes = plt.subplots(n_params, 1, figsize=(10, 6*n_params))
            fig.suptitle(f'Parameter Impact on {score_col}')
            
            if n_params == 1:
                axes = [axes]
            
            for ax, param in zip(axes, param_cols):
                ax.scatter(results[param], results[score_col])
                ax.set_xlabel(param)
                ax.set_ylabel(score_col)
                ax.grid(True)
            
            plt.tight_layout()
            plt.show()
        
        # 2. 如果是两个参数，为每个指标绘制热力图
        if n_params == 2:
            for score_col in score_cols:
                fig, ax = plt.subplots(figsize=(10, 8))
                
                pivot_table = results.pivot_table(
                    values=score_col, 
                    index=param_cols[0],
                    columns=param_cols[1]
                )
                
                im = ax.imshow(pivot_table, cmap='YlOrRd')
                plt.colorbar(im)
                
                ax.set_xticks(range(len(pivot_table.columns)))
                ax.set_yticks(range(len(pivot_table.index)))
                ax.set_xticklabels(pivot_table.columns)
                ax.set_yticklabels(pivot_table.index)
                
                ax.set_xlabel(param_cols[1])
                ax.set_ylabel(param_cols[0])
                ax.set_title(f'Parameter Combinations Heat Map - {score_col}')
                
                plt.tight_layout()
                plt.show()
        
    def _evaluate_parameters_multi_metric(self, params: Dict, 
                                        metrics: List[str] = None,
                                        config: Dict = None) -> Tuple[Dict, Dict]:
        """
        评估单个参数组合的多个指标
        """
        try:
            if config is None:
                config = {}
            if metrics is None:
                metrics = ['profit_factor']
            
            test_config = config.copy()
            
            # 更新配置中的参数
            for key, value in params.items():
                if '.' in key:
                    parts = key.split('.')
                    current_dict = test_config
                    for part in parts[:-1]:
                        if part not in current_dict:
                            current_dict[part] = {}
                        current_dict = current_dict[part]
                    current_dict[parts[-1]] = value
                else:
                    test_config[key] = value
            
            # 初始化策略并生成信号
            strategy = TradingStrategy(test_config)
            data = self.data_fetcher.get_historical_data(test_config)
            
            if data is None:
                return params, {metric: float('-inf') for metric in metrics}
            
            strategy.data = data
            strategy.indicators = Indicators(data)
            strategy.indicators.calculate_all_indicators()
            strategy.signals = SignalGenerator(data)
            strategy.signals.generate_all_signals()
            
            # 执行回测
            backtester = Backtester(test_config, self.initial_capital)
            backtester.run_backtest(strategy.data)
            results = backtester.generate_report()
            
            # 计算所有指标的分数
            scores = {}
            for metric in metrics:
                try:
                    if metric == 'sharpe_ratio':
                        # 简化夏普比率计算
                        initial_balance = self.initial_capital
                        final_balance = results.get('Final Balance', initial_balance)
                        total_return = (final_balance - initial_balance) / initial_balance
                        
                        if total_return >= 0:
                            scores[f'{metric}_score'] = total_return * 100  # 转换为百分比
                        else:
                            scores[f'{metric}_score'] = float('-inf')
                            
                    elif metric == 'profit_factor':
                        pf = results.get('Profit Factor', 0)
                        scores[f'{metric}_score'] = float(pf) if pf is not None else 0
                    elif metric == 'max_drawdown':
                        md = results.get('Max Drawdown (%)', 100)
                        scores[f'{metric}_score'] = float(-md) if md is not None else -100
                    elif metric == 'net_profit':
                        np_val = results.get('Net Profit', 0)
                        scores[f'{metric}_score'] = float(np_val) if np_val is not None else 0
                    else:
                        scores[f'{metric}_score'] = float('-inf')
                except Exception as e:
                    print(f"Error calculating {metric}: {str(e)}")
                    scores[f'{metric}_score'] = float('-inf')
            
            return params, scores
            
        except Exception as e:
            print(f"Error evaluating parameters: {str(e)}")
            return params, {f'{metric}_score': float('-inf') for metric in metrics}
        