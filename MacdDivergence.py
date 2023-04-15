import pandas as pd
import numpy as np
from StockStrategy import StockStrategy
import talib as ta
from StockDraw import StockDraw

#macd底背离策略
class MacdDivergence(StockStrategy):
    def __init__(self) -> None:
        super().__init__()

    def analyse(self, stockDF, stockCode, stockName):
        df = stockDF
        # 计算MACD指标
        df['MACD'], df['MACDsignal'], df['MACDhist'] = ta.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        # 计算金叉和死叉信号
        df['golden_cross'] = np.where(df['MACD'] > df['MACDsignal'], 1, 0)
        df['dead_cross'] = np.where(df['MACD'] < df['MACDsignal'], 1, 0)
        # 找到金叉和死叉的位置
        golden_cross_points = np.where(df['golden_cross'].diff() == 1)[0]
        dead_cross_points = np.where(df['dead_cross'].diff() == 1)[0]
        # 找到最近的两个金叉位置
        # 初始化底背离计数器
        divergence_count = 0
        # 存储底背离时间的列表
        divergence_dates = []
        # 检查每对相邻的金叉点
        for i in range(len(golden_cross_points) - 1):
            golden_cross_A = golden_cross_points[i]
            golden_cross_B = golden_cross_points[i + 1]
            macd_A = df.iloc[golden_cross_A]['MACD']
            macd_B = df.iloc[golden_cross_B]['MACD']
            low_A = df.iloc[golden_cross_A:golden_cross_A+2]['low'].min()
            low_B = df.iloc[golden_cross_B:golden_cross_B+2]['low'].min()

            date_A = pd.to_datetime(df.iloc[golden_cross_A]['date'])
            date_B = pd.to_datetime(df.iloc[golden_cross_B]['date'])
            date_diff = (date_B - date_A).days
            
            # 判断是否为底背离
            if macd_A < macd_B and low_A > low_B and date_diff >= 10:
                divergence_count += 1
                divergence_dates.append((df.iloc[golden_cross_A]['date'], df.iloc[golden_cross_B]['date']))


        # 输出底背离情况
        if divergence_count >= 2:
            print(stockCode + stockName + ' 至少存在两次底背离')
            print('底背离时间：')
            for i, (date_A, date_B) in enumerate(divergence_dates, 1):
                print(f'第{i}次底背离：{date_A} - {date_B}')

            stockDraw = StockDraw(df, 'macd')
            stockDraw.draw_candle_macd_turnover(stockName)             
