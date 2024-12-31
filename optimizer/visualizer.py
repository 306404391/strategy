import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
from mpl_toolkits.mplot3d import Axes3D

class OptimizationVisualizer:
    """优化结果可视化"""
    
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        self.results_df = self._prepare_data()
        
    def _prepare_data(self) -> pd.DataFrame:
        """准备数据"""
        # 将结果转换为DataFrame
        data = []
        for result in self.results:
            row = result['params'].copy()
            row.update({
                'score': result['score'],
                **{f"metric_{k}": v 
                   for k, v in result['metrics'].items() 
                   if isinstance(v, (int, float))}
            })
            data.append(row)
        return pd.DataFrame(data)
        
    def plot_parameter_distribution(self, figsize=(15, 10)) -> None:
        """绘制参数分布"""
        param_cols = [col for col in self.results_df.columns 
                     if not col.startswith(('score', 'metric_'))]
        n_params = len(param_cols)
        
        fig, axes = plt.subplots(n_params, 1, figsize=figsize)
        if n_params == 1:
            axes = [axes]
            
        for ax, param in zip(axes, param_cols):
            sns.scatterplot(data=self.results_df, x=param, y='score', ax=ax)
            ax.set_title(f'{param} vs Score')
            ax.grid(True)
            
        plt.tight_layout()
        plt.show()
        
    def plot_parameter_heatmap(self, param1: str, param2: str, 
                             figsize=(10, 8)) -> None:
        """绘制参数热力图"""
        pivot_table = self.results_df.pivot_table(
            values='score', 
            index=param1, 
            columns=param2, 
            aggfunc='mean'
        )
        
        plt.figure(figsize=figsize)
        sns.heatmap(pivot_table, annot=True, cmap='viridis', fmt='.3f')
        plt.title(f'Parameter Heatmap: {param1} vs {param2}')
        plt.show()
        
    def plot_3d_surface(self, param1: str, param2: str, 
                       figsize=(12, 8)) -> None:
        """绘制3D参数表面"""
        pivot_table = self.results_df.pivot_table(
            values='score', 
            index=param1, 
            columns=param2, 
            aggfunc='mean'
        )
        
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        X, Y = np.meshgrid(pivot_table.columns, pivot_table.index)
        Z = pivot_table.values
        
        surf = ax.plot_surface(X, Y, Z, cmap='viridis')
        fig.colorbar(surf)
        
        ax.set_xlabel(param2)
        ax.set_ylabel(param1)
        ax.set_zlabel('Score')
        plt.title(f'Parameter Surface: {param1} vs {param2}')
        plt.show()
        
    def plot_optimization_progress(self, figsize=(12, 6)) -> None:
        """绘制优化进度"""
        scores = [result['score'] for result in self.results]
        best_scores = np.maximum.accumulate(scores)
        
        plt.figure(figsize=figsize)
        plt.plot(scores, label='Score', alpha=0.5)
        plt.plot(best_scores, label='Best Score', linewidth=2)
        plt.title('Optimization Progress')
        plt.xlabel('Iteration')
        plt.ylabel('Score')
        plt.grid(True)
        plt.legend()
        plt.show()
        
    def plot_metric_correlations(self, figsize=(10, 8)) -> None:
        """绘制指标相关性"""
        metric_cols = [col for col in self.results_df.columns 
                      if col.startswith('metric_')]
        if not metric_cols:
            return
            
        corr_matrix = self.results_df[metric_cols].corr()
        
        plt.figure(figsize=figsize)
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Metric Correlations')
        plt.show()
        
    def plot_top_results(self, top_n: int = 10, figsize=(12, 6)) -> None:
        """绘制最佳结果"""
        top_results = self.results_df.nlargest(top_n, 'score')
        param_cols = [col for col in top_results.columns 
                     if not col.startswith(('score', 'metric_'))]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 参数分布
        for param in param_cols:
            ax1.scatter(top_results[param], 
                       [param] * len(top_results), 
                       alpha=0.6)
        ax1.set_title('Parameter Values in Top Results')
        ax1.grid(True)
        
        # 得分分布
        ax2.bar(range(top_n), top_results['score'])
        ax2.set_title('Top Scores')
        ax2.set_xlabel('Rank')
        ax2.set_ylabel('Score')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()
        
    def generate_report(self) -> None:
        """生成完整的优化报告"""
        print("=== Optimization Report ===")
        
        # 打印最佳结果
        best_result = max(self.results, key=lambda x: x['score'])
        print("\nBest Parameters:")
        for param, value in best_result['params'].items():
            print(f"{param}: {value}")
        print(f"\nBest Score: {best_result['score']:.4f}")
        
        # 打印关键指标
        print("\nBest Result Metrics:")
        for key, value in best_result['metrics'].items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
                
        # 绘制可视化
        print("\nGenerating visualizations...")
        self.plot_optimization_progress()
        self.plot_parameter_distribution()
        self.plot_metric_correlations()
        self.plot_top_results()
        
        # 如果有两个以上参数，绘制热力图
        param_cols = [col for col in self.results_df.columns 
                     if not col.startswith(('score', 'metric_'))]
        if len(param_cols) >= 2:
            self.plot_parameter_heatmap(param_cols[0], param_cols[1])
            self.plot_3d_surface(param_cols[0], param_cols[1]) 