from StockStrategy import StockStrategy

#穿越年线模型
#1. 5日上穿170后的回踩
#2. vol一直低迷，偶尔有3倍爆量
#3. 筹码集中度90%的 在15%以下
class CrossYear(StockStrategy):
    def __init__(self) -> None:
        super().__init__()

    def analyse(self, stockDf, stockCode, stockName):
        bRturn = False
        # 获取均线
        stockDf['MA5'] = stockDf['close'].rolling(5).mean()
        stockDf['MA34'] = stockDf['close'].rolling(34).mean()
        stockDf['MA170'] = stockDf['close'].rolling(170).mean()

        # 计算90日平均成交量
        stockDf['MA90_Volume'] = stockDf['volume'].rolling(90).mean()

        # 最近30天内5日线上穿170日线
        cross_days = []
        for i in range(len(stockDf) - 30, len(stockDf) - 1):
            if stockDf.loc[i, 'MA5'] <= stockDf.loc[i, 'MA170'] and stockDf.loc[i + 1, 'MA5'] > stockDf.loc[i + 1, 'MA170']:
                cross_days.append(i)

        # 90日内成交量一直很小，只有1-5天的成交量是90日平均成交量的2倍及以上
        low_volume_days = []
        for i in range(len(stockDf) - 90, len(stockDf)):
            if stockDf.loc[i, 'volume'] < 1.5 * stockDf.loc[i, 'MA90_Volume']:
                low_volume_days.append(i)

        if len(low_volume_days) >= 85 and len(low_volume_days) < 90 and len(cross_days) > 0:
            #cc = self.calculate_chip_concentration(stockDf.tail(340))
            if self.priceFluct(stockDf) :
                print(stockCode + stockName + "符合穿越年线策略")
                bRturn = True
        else:
            bRturn = False

        return bRturn
        
    def calculate_chip_concentration(self, df, price_interval=1.0, concentration_percentage=80):
        # 创建一个新的 DataFrame 副本以避免 SettingWithCopyWarning
        df = df.copy()

        # 创建一个新列 'price_level'，将收盘价按照设定的价格区间进行分组
        df.loc[:, 'price_level'] = (df['close'] // price_interval) * price_interval

        # 计算每个价格区间的总成交量
        grouped_df = df.groupby('price_level').sum(numeric_only=True).reset_index()

        # 对成交量进行降序排序
        sorted_df = grouped_df.sort_values(by='volume', ascending=False)

        # 计算总成交量
        total_volume = sorted_df['volume'].sum()

        # 计算筹码集中度
        percentage_volume = 0
        chip_concentration = 0
        for index, row in sorted_df.iterrows():
            percentage_volume += row['volume']
            chip_concentration += 1
            if percentage_volume / total_volume * 100 >= concentration_percentage:
                break

        return chip_concentration / len(sorted_df)


    
    def priceFluct(self, stockDf):
        last_120_to_30 = stockDf[-120:-30]
        high_max = last_120_to_30['high'].max()
        low_min = last_120_to_30['low'].min()

        price_fluctuation = (high_max - low_min) / low_min
        if price_fluctuation <= 0.2:
            return True
        else:
            return False




        
