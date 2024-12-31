"""
交易信号生成模块，负责根据技术指标生成买卖信号
"""

class SignalGenerator:
    """交易信号生成器，根据多种技术指标生成交易信号"""
    
    def __init__(self, data):
        """
        初始化信号生成器
        :param data: 包含技术指标数据的DataFrame
        """
        self.data = data

    def generate_long_signals(self):
        """
        生成多头（买入）信号，需满足以下条件：
        1. 价格突破唐奇安通道上轨
        2. 价格突破布林带上轨
        3. 凯尔特纳通道中轨上升
        4. ATR上升
        5. 乔金波动率上升
        6. RVI > 60且上穿信号线
        """
        self.data['short_signal'] = (
            # (self.data['close'] > self.data['DC_upper']) &
            # (self.data['close'] > self.data['BB_upper']) &
            # (self.data['KC_middle'].diff() > 0) &
            # (self.data['ATR'].diff() > 0) &
            # (self.data['Volatility_Chaikin'].diff() > 0) &
            (self.data['RVI'] > 60) &
            (self.data['RVI'] > self.data['RVI_signal'])
        )

    # def generate_long_signals(self):
    #     """
    #     生成多头（买入）信号，需满足以下条件：
    #     1. 价格突破唐奇安通道上轨
    #     2. 价格突破布林带中轨
    #     3. 凯尔特纳通道中轨上升
    #     4. ATR上升
    #     5. 乔金波动率上升
    #     6. RVI 上穿信号线
    #     """
    #     self.data['long_signal'] = (
    #         # self.data['close'] > self.data['DC_upper']
    #         self.data['close'] > self.data['BB_middle']
    #         # (self.data['KC_middle'].diff() > 0) &
    #         # (self.data['ATR'].diff() > 0) &
    #         # (self.data['Volatility_Chaikin'].diff() > 0) &
    #         # (self.data['RVI'] > self.data['RVI_signal'])
    #     )

    def generate_short_signals(self):
        """
        生成空头（卖出）信号，需满足以下条件：
        1. 价格突破唐奇安通道下轨
        2. 价格突破布林带下轨
        3. 凯尔特纳通道中轨下降
        4. ATR上升
        5. 乔金波动率上升
        6. RVI < 40且下穿信号线
        """
        self.data['long_signal'] = (
            # (self.data['close'] < self.data['DC_lower']) &
            # (self.data['close'] < self.data['BB_lower']) &
            # (self.data['KC_middle'].diff() < 0) &
            # (self.data['ATR'].diff() > 0) &
            # (self.data['Volatility_Chaikin'].diff() > 0) &
            (self.data['RVI'] < 40) &
            (self.data['RVI'] < self.data['RVI_signal'])
        )

    # def generate_short_signals(self):
    #     """
    #     生成空头（卖出）信号，需满足以下条件：
    #     1. 价格突破唐奇安通道下轨
    #     2. 价格突破布林带中轨
    #     3. 凯尔特纳通道中轨下降
    #     4. ATR上升
    #     5. 乔金波动率上升
    #     6. RVI 下穿信号线
    #     """
    #     self.data['short_signal'] = (
    #         # self.data['close'] < self.data['DC_lower']
    #         self.data['close'] < self.data['BB_middle']
    #         # (self.data['KC_middle'].diff() < 0) &
    #         # (self.data['ATR'].diff() > 0) &
    #         # (self.data['Volatility_Chaikin'].diff() > 0) &
    #         # (self.data['RVI'] < self.data['RVI_signal'])
    #     )

    def filter_signals(self):
        """
        过滤交易信号，添加额外条件：
        1. 成交量需高于20周期平均成交量
        """
        # 使用tick_volume作为交易量指标
        self.data['long_signal'] = self.data['long_signal'] & (
            self.data['tick_volume'] > self.data['tick_volume'].rolling(20).mean()
        )
        self.data['short_signal'] = self.data['short_signal'] & (
            self.data['tick_volume'] > self.data['tick_volume'].rolling(20).mean()
        )

    def generate_all_signals(self):
        """生成所有交易信号，包括多头、空头信号和过滤"""
        self.generate_long_signals()
        self.generate_short_signals()
        # self.filter_signals()
        
        # 打印信号统计信息
        long_count = self.data['long_signal'].sum()
        short_count = self.data['short_signal'].sum()
        print(f"Generated signals - Long: {long_count}, Short: {short_count}")
