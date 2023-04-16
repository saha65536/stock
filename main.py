#主入口函数
from StockData import StockData
from MacdDivergence import MacdDivergence
from BackTest import stock_strategy_test
from datetime import datetime, timedelta


def dateCut(date_B, daycut):   
    date_format = "%Y-%m-%d"  # 定义日期格式

    # 将字符串转换为datetime对象
    date_B_datetime = datetime.strptime(date_B, date_format)

    # 往后推60天
    date_B_datetime_plus = date_B_datetime + timedelta(days=daycut)

    # 将datetime对象转回为字符串
    date_B_str_plus = date_B_datetime_plus.strftime(date_format)

    return date_B_str_plus

if __name__ == '__main__':
    stockData = StockData('2022-07-01', '2022-12-31', 2)
    dfList = stockData.getStocksList()
    result = 0.0
    for index, row in dfList.iterrows():
        stockCode = row['code']
        stockName = row['code_name']
        macdIns = MacdDivergence()
        dfOne = stockData.getOneStockData(stockCode)
        stockCode, date_B = macdIns.analyse(dfOne, stockCode, stockName)
        if stockCode != '':
            stockDataTest = StockData(dateCut(date_B,-5), dateCut(date_B,60), 2)
            dfTest = stockDataTest.getOneStockData(stockCode)
            result += stock_strategy_test(date_B, dfTest)

    print(result)



        