from typing import Dict, List, Any, Tuple
import numpy as np
import random
from .base import BaseOptimizer

class GeneticOptimizer(BaseOptimizer):
    """遗传算法优化器"""
    
    def __init__(self, *args, 
                 population_size: int = 50,
                 generations: int = 30,
                 mutation_rate: float = 0.1,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        
    def optimize(self) -> Dict[str, Any]:
        """执行遗传算法优化"""
        # 初始化种群
        population = self._initialize_population()
        
        for generation in range(self.generations):
            # 评估适应度
            fitness_scores = [self.evaluate_params(p) for p in population]
            
            # 选择父代
            parents = self._select_parents(population, fitness_scores)
            
            # 生成新一代
            new_population = []
            while len(new_population) < self.population_size:
                # 交叉
                parent1, parent2 = random.sample(parents, 2)
                child = self._crossover(parent1, parent2)
                
                # 变异
                if random.random() < self.mutation_rate:
                    child = self._mutate(child)
                    
                new_population.append(child)
                
            population = new_population
            
        return self.get_best_params()
        
    def _initialize_population(self) -> List[Dict[str, Any]]:
        """初始化种群"""
        population = []
        for _ in range(self.population_size):
            params = {}
            for name, values in self.param_space.items():
                params[name] = random.choice(values)
            population.append(params)
        return population
        
    def _select_parents(self, population: List[Dict[str, Any]], 
                       fitness_scores: List[float]) -> List[Dict[str, Any]]:
        """选择父代"""
        # 使用轮盘赌选择
        total_fitness = sum(max(0, score) for score in fitness_scores)
        if total_fitness == 0:
            return random.sample(population, len(population) // 2)
            
        probs = [max(0, score) / total_fitness for score in fitness_scores]
        return random.choices(population, weights=probs, k=len(population) // 2)
        
    def _crossover(self, parent1: Dict[str, Any], 
                  parent2: Dict[str, Any]) -> Dict[str, Any]:
        """交叉操作"""
        child = {}
        for param_name in self.param_space.keys():
            # 随机选择父代的参数
            child[param_name] = random.choice([parent1[param_name], parent2[param_name]])
        return child
        
    def _mutate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """变异操作"""
        mutated = params.copy()
        param_name = random.choice(list(self.param_space.keys()))
        mutated[param_name] = random.choice(self.param_space[param_name])
        return mutated 