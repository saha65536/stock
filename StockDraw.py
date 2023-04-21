import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import os
import matplotlib.ticker as ticker
from StockData import StockData


class StockDraw:
    def __init__(self, dfIn, strategyName):
        self.df = dfIn
        self.strategyName = strategyName

        # 检查 result 文件夹下是否有 strategyName 文件夹
        self.strategy_path = os.path.join("result", self.strategyName)
        if not os.path.exists(self.strategy_path):
            os.makedirs(self.strategy_path)
        self.strategy_path = self.strategy_path + "/"

    def draw_candlestick(self, ax):
        ohlc = self.df[['date', 'open', 'high', 'low', 'close']].copy()
        ohlc['date'] = pd.to_datetime(ohlc['date'])
        ohlc['date_idx'] = range(len(ohlc))  # 添加整数索引
        ohlc = ohlc[['date_idx', 'open', 'high', 'low', 'close']].values.tolist()
        candlestick_ohlc(ax, ohlc, width=0.7, colorup='red', colordown='green')

        # 计算移动平均线
        ma_5 = self.df['close'].rolling(window=5).mean()
        ma_34 = self.df['close'].rolling(window=34).mean()

        # 绘制移动平均线
        ax.plot(range(len(self.df)), ma_5, label='5-Day MA', color='blue', linewidth=1)
        ax.plot(range(len(self.df)), ma_34, label='34-Day MA', color='purple', linewidth=1)

        ax.set_title('Stock Price')
        ax.grid(True)
        ax.legend(loc='best')

        date_idx_to_date = self.df['date'].reset_index(drop=True).to_dict()  # 整数索引到日期的映射
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, prune='both'))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: date_idx_to_date.get(x, '')))  # 使用自定义刻度标签

    
    def draw_macd(self, ax):
        df = self.df
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        ax.plot(df['date'], macd, label='MACD', color='red')
        ax.plot(df['date'], signal, label='Signal Line', color='blue')

        ax.legend(loc='upper left')
        ax.set_title('MACD')
        ax.grid(True)

        # 仅显示具有成交数据的日期
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, prune='both'))


    def draw_kdj(self, ax):
        df = self.df
        low_list = df['low'].rolling(9, min_periods=9).min()
        high_list = df['high'].rolling(9, min_periods=9).max()
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d

        overbought = 80
        oversold = 20

        overbought_regions = (k > overbought) & (d > overbought)
        oversold_regions = (k < oversold) & (d < oversold)

        ax.plot(df['date'], k, label='K Line', color='blue')
        ax.plot(df['date'], d, label='D Line', color='green')
        ax.plot(df['date'], j, label='J Line', color='red')

        for idx, (start, end) in enumerate(zip(df['date'][overbought_regions], df['date'][overbought_regions.shift(-1).fillna(False)])):
            if idx % 2 == 0:
                ax.add_patch(Rectangle((start, overbought), end - start, 100 - overbought, edgecolor=None, facecolor='purple', alpha=0.3))
        for idx, (start, end) in enumerate(zip(df['date'][oversold_regions], df['date'][oversold_regions.shift(-1).fillna(False)])):
            if idx % 2 == 0:
                ax.add_patch(Rectangle((start, 0), end - start, oversold, edgecolor=None, facecolor='purple', alpha=0.3))

        ax.legend(loc='upper left')
        ax.set_title('KDJ')
        ax.grid(True)

        # 仅显示具有成交数据的日期
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, prune='both'))


    def draw_turnover(self, ax):
        df = self.df
        try:
            df['volume'] = df['volume'].astype(float)
        except ValueError:
            for value in df['volume']:
                print(value)
        df['close'] = df['close'].astype(float)
        turnover = df['volume'] * df['close']

        # 计算 5 日和 10 日平均成交额
        turnover_ma5 = turnover.rolling(window=5).mean()
        turnover_ma10 = turnover.rolling(window=10).mean()

        # 绘制成交额柱状图
        ax.bar(df['date'], turnover, label='Turnover', color='red', alpha=0.7)

        # 绘制 5 日和 10 日平均成交额折线图
        ax.plot(df['date'], turnover_ma5, label='5-day MA', color='blue')
        ax.plot(df['date'], turnover_ma10, label='10-day MA', color='orange')

        
        ax.legend(loc='upper left')
        ax.set_title('Daily Turnover')
        ax.grid(True)

        # 仅显示具有成交数据的日期
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, prune='both'))

    #画OBV量化指标On-Balance Volume（OBV）是一种技术分析指标，用于衡量成交量与价格变动的关系，以评估资金流入和流出的动态。OBV的计算方法如下：
    #
    #如果当天的收盘价比前一天高，则OBV等于前一天的OBV加上当天的成交量。
    #如果当天的收盘价比前一天低，则OBV等于前一天的OBV减去当天的成交量。
    #如果当天的收盘价与前一天相同，则OBV保持不变。

    def draw_obv(self, ax):
        df = self.df
        try:
            df['volume'] = df['volume'].astype(float)
        except ValueError:
            for value in df['volume']:
                print(value)
        df['close'] = df['close'].astype(float)
        
        # 计算OBV
        obv = [0]
        for i in range(1, len(df)):
            if df['close'][i] > df['close'][i - 1]:
                obv.append(obv[-1] + df['volume'][i])
            elif df['close'][i] < df['close'][i - 1]:
                obv.append(obv[-1] - df['volume'][i])
            else:
                obv.append(obv[-1])

        df['obv'] = obv

        # 计算 5 日和 10 日平均OBV
        obv_ma5 = df['obv'].rolling(window=5).mean()
        obv_ma10 = df['obv'].rolling(window=10).mean()

        # 绘制OBV折线图
        ax.plot(df['date'], df['obv'], label='OBV', color='red', alpha=0.7)

        # 绘制 5 日和 10 日平均OBV折线图
        ax.plot(df['date'], obv_ma5, label='5-day MA', color='blue')
        ax.plot(df['date'], obv_ma10, label='10-day MA', color='orange')

        ax.legend(loc='upper left')
        ax.set_title('On Balance Volume (OBV)')
        ax.grid(True)

        # 仅显示具有成交数据的日期
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, prune='both'))



    def draw_macd_kdj(self, stock_code):
        df = self.df

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))

        self.draw_candlestick(ax1)
        self.draw_macd(ax2)
        self.draw_kdj(ax3)

        plt.savefig(self.strategy_path + stock_code + ".jpg")   

    def draw_macd_candle(self, stock_code):
        df = self.df

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        self.draw_candlestick(ax1)
        self.draw_macd(ax2)

        plt.savefig(self.strategy_path + stock_code + ".jpg") 

    def draw_candle_macd_turnover(self, stock_code, date_last):
        df = self.df

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))

        self.draw_candlestick(ax1)
        self.draw_macd(ax2)
        self.draw_turnover(ax3)

        plt.savefig(self.strategy_path + stock_code + "_" + date_last + ".jpg")

    def draw_candle_macd_obv(self, stock_code, date_last):
        df = self.df

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))

        self.draw_candlestick(ax1)
        self.draw_macd(ax2)
        self.draw_obv(ax3)

        plt.savefig(self.strategy_path + stock_code + "_" + date_last + ".jpg")

if __name__ == '__main__':
    stockData = StockData('2022-10-01', '2023-04-21', 2)
    dfOne = stockData.getOneStockData('sh.601127')
    stockDraw = StockDraw(dfOne, 'macd')
    stockDraw.draw_candle_macd_obv('赛力斯', '2023-04-21')


