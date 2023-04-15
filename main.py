#主入口函数
from StockData import StockData
from MacdDivergence import MacdDivergence


if __name__ == '__main__':
    stockData = StockData('2022-11-01', '2023-04-13', 2)
    dfList = stockData.getStocksList()
    print(len(dfList))
    for index, row in dfList.iterrows():
        stockCode = row['code']
        stockName = row['code_name']
        macdIns = MacdDivergence()
        dfOne = stockData.getOneStockData(stockCode)
        macdIns.analyse(dfOne, stockCode, stockName)