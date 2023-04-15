import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

class StockDraw:
    def __init__(self, dfIn):
        self.df = dfIn

    def draw(self, stock_code):
        # 获取指定股票代码的数据
        df = self.df
        df['date'] = pd.to_datetime(df['date'])

        # 计算 MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()

        # 计算 KDJ
        low_list = df['low'].rolling(9, min_periods=9).min()
        high_list = df['high'].rolling(9, min_periods=9).max()
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d

        # 超买和超卖阈值
        overbought = 80
        oversold = 20

        # 找到超买和超卖的区间
        overbought_regions = (k > overbought) & (d > overbought)
        oversold_regions = (k < oversold) & (d < oversold)

        # 将股票数据转换为 OHLC（开盘价、最高价、最低价、收盘价）格式
        ohlc = df[['date', 'open', 'high', 'low', 'close']].copy()
        ohlc['date'] = mdates.date2num(ohlc['date'].dt.to_pydatetime())
        ohlc = ohlc.values.tolist()

        # 绘制蜡烛图、MACD和KDJ图表
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
        candlestick_ohlc(ax1, ohlc, width=0.7, colorup='red', colordown='green')
        ax1.set_title('Stock Price')
        ax1.xaxis_date()
        ax1.grid(True)

        ax2.plot(df['date'], macd, label='MACD', color='red')
        ax2.plot(df['date'], signal, label='Signal Line', color='blue')
        ax2.legend(loc='upper left')
        ax2.set_title('MACD')
        ax2.xaxis_date()
        ax2.grid(True)

        ax3.plot(df['date'], k, label='K Line', color='blue')
        ax3.plot(df['date'], d, label='D Line', color='green')
        ax3.plot(df['date'], j, label='J Line', color='red')

        # 画超买超卖矩形区域
        for idx, (start, end) in enumerate(zip(df['date'][overbought_regions], df['date'][overbought_regions.shift(-1).fillna(False)])):
            if idx % 2 == 0:
                ax3.add_patch(Rectangle((start, overbought), end - start, 100 - overbought, edgecolor=None, facecolor='purple', alpha=0.3))
        for idx, (start, end) in enumerate(zip(df['date'][oversold_regions], df['date'][oversold_regions.shift(-1).fillna(False)])):
            if idx % 2 == 0:
                ax3.add_patch(Rectangle((start, 0), end - start, oversold, edgecolor=None, facecolor='purple', alpha=0.3))

        ax3.legend(loc='upper left')
        ax3.set_title('KDJ')
        ax3.xaxis_date()
        ax3.grid(True)

        # 将图像保存为文件
        plt.savefig("./result/macd/" + stock_code + ".jpg")



