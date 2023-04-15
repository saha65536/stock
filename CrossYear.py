from StockStrategy import StockStrategy

#穿越年线模型
#1. 5日上穿170后的回踩
#2. vol一直低迷，偶尔有3倍爆量
#3. 筹码集中度90%的 在15%以下
class CrossYear(StockStrategy):
    def __init__(self) -> None:
        super().__init__()

    def analyse(self, stockDf):
        #获取均线
        df = []
        tmpDf5 = stockDf.rolling(5, 5).mean()
        df['MA5'] = tmpDf5['Close']
        tmpDf34 = stockDf.rolling(34, 34).mean()
        df['MA34'] = tmpDf34['Close']
        tmpDf170 = stockDf.rolling(170, 170).mean()   
        df['MA170'] = tmpDf170['Close']
        
