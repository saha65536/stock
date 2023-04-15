import pandas as pd# 导入DataFrame数据 

class EntanglementTheoryCenter:
    def __init__(self, code):
        self.code = code
        self.amtWindows = 70
        self.lastCheck = 20
        self.readData()
    
    def readData(self):
        # 导入股票数据    
        self.df = pd.read_csv('data/'+ self.code + '.csv')
        # 格式化列名，用于之后的绘制，左边的列名修改为右边的
        self.df.rename(
                columns={
                'date': 'od', 'open': 'Open', 
                'high': 'High', 'low': 'Low', 
                'close': 'Close', 'amount': 'Amount'}, 
                inplace=True)
        # 转换为日期格式
        self.df['Date'] = pd.to_datetime(self.df['od'])
        # 将日期列作为行索引
        self.df.set_index(['Date'], inplace=True)
        
        #获取均线
        tmpDf = self.df.rolling(5, 5).mean()
        self.df['MA5'] = tmpDf['Close']
        tmpDf=self.df.rolling(34, 34).mean()
        self.df['MA34'] = tmpDf['Close']
        tmpDf=self.df.rolling(170, 170).mean()   
        self.df['MA170'] = tmpDf['Close']
        
    def judgeAmountLevel(self):
        topAmt = self.df['Amount'].rolling(self.amtWindows).max() 
        self.df['topAmt'] = topAmt
        dfTmp = self.df.where(self.df['topAmt'] == self.df['Amount'],0)
        self.df['peak'] = dfTmp['topAmt']
        
        for i in range(len(self.df) -self.lastCheck,len(self.df)):
            if self.df.iloc[i]['peak'] != 0:
                pMax = self.df.iloc[i-60:i]['Amount'].max()
                if  pMax*2 > self.df.iloc[i]['peak'] and pMax*1.5 < self.df.iloc[i]['peak']:
                    print(self.df.iloc[i]['od'])
                    return True
                else:
                    break
            else:
                continue
        return False
