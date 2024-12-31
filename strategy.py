from indicators import Indicators
from signal_generator import SignalGenerator
from trade_executor import TradeExecutor
from risk_manager import RiskManager
from logger import TradeLogger
from backtester import Backtester
from datetime import datetime


"""
策略模式实现模块，包含交易策略、实时执行器和回测执行器
"""

from datetime import datetime
from indicators import Indicators
from signal_generator import SignalGenerator
from trade_executor import TradeExecutor
from risk_manager import RiskManager
from logger import TradeLogger
from backtester import Backtester

class TradingStrategy:
    """交易策略类，负责准备数据和执行策略"""
    
    def __init__(self, config):
        """
        初始化交易策略
        :param config: 配置字典，包含策略参数
        """
        self.config = config
        self.data = None  # 存储市场数据
        self.indicators = None  # 存储技术指标
        self.signals = None  # 存储交易信号

    def prepare_data(self, data_fetcher):
        """
        准备交易数据，包括获取数据、计算指标和生成信号
        :param data_fetcher: 数据获取器实例
        """
        # 获取历史数据
        self.data = data_fetcher.get_historical_data(self.config)
        
        if self.data is None or len(self.data) == 0:
            raise ValueError("Failed to get historical data")
        
        # 计算技术指标
        self.indicators = Indicators(self.data)
        self.indicators.calculate_all_indicators()

        # 生成交易信号
        self.signals = SignalGenerator(self.data)
        self.signals.generate_all_signals()

    def execute(self, executor):
        """
        执行交易策略
        :param executor: 执行器实例（LiveExecutor或BacktestExecutor）
        """
        # 遍历数据，根据信号执行交易
        for index, row in self.data.iterrows():
            if row['long_signal'] or row['short_signal']:
                executor.execute_trade(row)

class LiveExecutor:
    """实时交易执行器，负责执行实时交易操作"""
    
    def __init__(self, config):
        """
        初始化实时交易执行器
        :param config: 配置字典，包含交易参数
        """
        # 初始化交易执行模块
        self.trade_executor = TradeExecutor(
            symbol=config['symbol'],
            magic_number=config['trading']['magic_number']
        )
        # 初始化风险管理模块
        self.risk_manager = RiskManager(
            account_balance=10000,
            risk_percentage=config['risk_management']['risk_percentage'],
            max_open_trades=config['risk_management']['max_open_trades']
        )
        # 初始化日志记录模块
        self.logger = TradeLogger()

    def execute_trade(self, row):
        """
        执行单笔交易
        :param row: 包含交易信号和指标数据的行
        """
        # 检查是否可以开新仓
        if self.risk_manager.can_open_trade(self.trade_executor.get_open_positions()):
            # 计算仓位大小
            position_size = self.risk_manager.calculate_position_size(
                row['ATR'],
                self.config['risk_management']['stop_loss_multiplier']
            )
            # 执行交易
            trade_result = self.trade_executor.manage_trades(row)
            # 记录交易日志
            if trade_result:
                self.logger.log_trade(trade_result)

class BacktestExecutor:
    """回测执行器，负责执行策略回测"""
    
    def __init__(self, data, config):
        """
        初始化回测执行器
        :param data: 回测使用的历史数据
        :param config: 策略配置
        """
        self.backtester = Backtester(config)
        self.data = data
        # 在初始化时运行回测
        self.backtester.run_backtest(data)

    def execute_trade(self, row):
        """
        执行回测交易
        :param row: 包含交易信号和指标数据的行
        """
        # 回测已在初始化时运行，这里不需要执行任何操作
        pass

    def get_report(self):
        """
        获取回测报告
        :return: 包含回测结果的字典
        """
        return self.backtester.generate_report()

    def plot_results(self):
        """绘制回测结果图表"""
        self.backtester.plot_equity_curve()
