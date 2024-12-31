"""
风险管理模块，负责仓位计算和风险控制
"""

class RiskManager:
    """风险管理器，负责计算仓位大小和控制风险暴露"""
    
    def __init__(self, account_balance, risk_percentage=0.02, max_open_trades=5):
        """
        初始化风险管理器
        :param account_balance: 账户余额
        :param risk_percentage: 单笔交易风险比例，默认为2%
        :param max_open_trades: 最大同时持仓数量，默认为5
        """
        self.account_balance = account_balance
        self.risk_percentage = risk_percentage
        self.max_open_trades = max_open_trades

    def calculate_position_size(self, atr, stop_loss_multiplier=1.5):
        """
        计算仓位大小
        :param atr: 平均真实波动幅度
        :param stop_loss_multiplier: 止损倍数，默认为1.5
        :return: 计算出的仓位大小
        """
        # 计算风险金额
        risk_amount = self.account_balance * self.risk_percentage
        # 计算仓位大小
        position_size = risk_amount / (atr * stop_loss_multiplier)
        return round(position_size, 2)

    def adjust_position_size(self, atr, market_volatility):
        """
        根据市场波动性动态调整仓位大小
        :param atr: 平均真实波动幅度
        :param market_volatility: 市场波动性，'high'、'low'或None
        :return: 调整后的仓位大小
        """
        if market_volatility == 'high':
            # 高波动性时使用更大的止损倍数
            return self.calculate_position_size(atr, stop_loss_multiplier=2.0)
        elif market_volatility == 'low':
            # 低波动性时使用更小的止损倍数
            return self.calculate_position_size(atr, stop_loss_multiplier=1.0)
        else:
            # 默认情况
            return self.calculate_position_size(atr)

    def can_open_trade(self, current_open_trades):
        """
        检查是否可以开新仓
        :param current_open_trades: 当前持仓列表
        :return: 如果可以开新仓返回True，否则返回False
        """
        return len(current_open_trades) < self.max_open_trades

    def update_account_balance(self, new_balance):
        """
        更新账户余额
        :param new_balance: 新的账户余额
        """
        self.account_balance = new_balance
