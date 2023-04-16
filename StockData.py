import pandas as pd
import baostock as bs
import os
import sqlite3

#股票数据类，下载数据并保存到文件
class StockData:
    CSV_TYPE = 1
    DB_TYPE = 2
    DBNAME = 'D:/sqlite/data/stocks_db.db'

    def __init__(self, beg_date, end_date, dataType):
        if dataType == StockData.CSV_TYPE:
            lg = bs.login()
            print('login respond error_code:'+lg.error_code)
            print('login respond  error_msg:'+lg.error_msg) 
        self.__dataStoreDir__ = './data/'
        self.__resultStoreDir__ = './result/'
        self.__beg_date__ = beg_date
        self.__end_date__ = end_date
        self.__data_type__ = dataType 
        if dataType == StockData.DB_TYPE:
            # 创建一个SQLite3连接
            try:
                self.conn = sqlite3.connect(StockData.DBNAME)
                print("数据库连接成功")
            except sqlite3.Error as e:
                print("数据库连接失败：", e)

    def __del__(self):
        if self.__data_type__ == StockData.DB_TYPE:
            self.conn.close()
            print("数据库已关闭")

    def downloadData(self):
        self.__getList__()
        self.__getStocks__()
    
        
    def __makeDIR__(self,dirName):
        if not os.path.exists(dirName):
            os.mkdir(dirName)


    def updateStocks(self):
        stocks = []    
        # 获取中证500成分股
        rs = bs.query_zz500_stocks()
        print('query_zz500 error_code:'+rs.error_code)
        print('query_zz500  error_msg:'+rs.error_msg)    
        
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            stocks.append(rs.get_row_data())

        result = pd.DataFrame(stocks, columns=rs.fields)
        result.to_sql('stocks_zz500', self.conn, if_exists='replace', index=False)
            
        # 获取沪深300成分股
        stocks.clear()
        rs = bs.query_hs300_stocks()
        print('query_hs300 error_code:'+rs.error_code)
        print('query_hs300  error_msg:'+rs.error_msg)    
        
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            stocks.append(rs.get_row_data())
            stocks.append(rs.get_row_data())
        result = pd.DataFrame(stocks, columns=rs.fields)
        result.to_sql('stocks_hs300', self.conn, if_exists='replace', index=False)
            
        
    
    def __getList__(self):
        stocks = []    
        # 获取中证500成分股
        rs = bs.query_zz500_stocks()
        print('query_zz500 error_code:'+rs.error_code)
        print('query_zz500  error_msg:'+rs.error_msg)    
        
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            stocks.append(rs.get_row_data())
            
        # 获取沪深300成分股
        rs = bs.query_hs300_stocks()
        print('query_hs300 error_code:'+rs.error_code)
        print('query_hs300  error_msg:'+rs.error_msg)    
        
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            stocks.append(rs.get_row_data())
            stocks.append(rs.get_row_data())
            
        result = pd.DataFrame(stocks, columns=rs.fields)
        # 结果集输出到csv文件
        
        self.__makeDIR__(self.__dataStoreDir__)
        result.to_csv(self.__dataStoreDir__ + 'stocks.csv', index=False)

    #获取每个股票数据
    def __getStocks__(self):         
        dfall = self.getStocksList()
        for i in range(0,len(dfall)):
            print('begin read :' + str(i) + ' '+ dfall.iloc[i]['code']   + ' '+ dfall.iloc[i]['code_name'])
            self.__read_onestock__(dfall.iloc[i]['code'])
            if i % 50 == 0:
                self.conn.commit()
        

    def __insert_into_db__(self, df):     
        # 将DataFrame数据插入到SQLite3数据库的表中
        df.to_sql('stock_day_data', self.conn, if_exists='append', index=False,
                dtype={'date': 'TEXT', 'code': 'TEXT', 'open': 'REAL', 'high': 'REAL',
                        'low': 'REAL', 'close': 'REAL', 'preclose': 'REAL', 'volume': 'INTEGER',
                        'amount': 'REAL', 'adjustflag': 'INTEGER', 'turn': 'REAL', 'tradestatus': 'INTEGER',
                        'pctChg': 'REAL', 'isST': 'INTEGER'})


  

    
    #读取一只股票的数据    
    def __read_onestock__(self, stock_code):    
        
        if os.path.isfile('data/'+ stock_code + '.csv'):
            return
        
        # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
        # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
        rs = bs.query_history_k_data_plus(stock_code,
            "date,code,open,high,low,close,preclose,volume"+
            ",amount,adjustflag,turn,tradestatus,pctChg,isST",
            start_date = self.__beg_date__, end_date = self.__end_date__,
            frequency="d", adjustflag="2")
        
        # 打印结果集
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)

        if self.__data_type__ == StockData.DB_TYPE:
            self.__insert_into_db__(result)   
        elif self.__data_type__ == StockData.CSV_TYPE:       
            result.to_csv(self.__dataStoreDir__ + stock_code + '.csv', index=False) 

    def getOneStockData(self, stockCode):
        if self.__data_type__ == StockData.CSV_TYPE: 
            df = pd.read_csv('./data/' + stockCode + '.csv')
            # 格式化列名，用于之后的绘制
            df.rename(
                    columns={
                    'date': 'od', 'open': 'Open', 
                    'high': 'High', 'low': 'Low', 
                    'close': 'Close', 'volume': 'Volume'}, 
                    inplace=True)
            # 转换为日期格式
            df['Date'] = pd.to_datetime(df['od'])
            # 将日期列作为行索引
            df.set_index(['Date'], inplace=True)
            return df
        elif self.__data_type__ == StockData.DB_TYPE:       
            read_sql = ("SELECT * FROM stock_day_data where code ='" + stockCode + "'"
            " and date > '" + self.__beg_date__ + "'"  
            " and date < '" + self.__end_date__ + "' order by date asc")   
            df = pd.read_sql_query(read_sql, self.conn)
            return df
        
    def getStocksList(self):
        if self.__data_type__ == StockData.CSV_TYPE:
            dfall = pd.read_csv('data/'+ 'stocks.csv')
            return dfall
        elif self.__data_type__ == StockData.DB_TYPE:
            df = pd.read_sql_query("select * from stocks_hs300 UNION ALL SELECT * from stocks_zz500", self.conn)
            return df            

      
    
if __name__ == '__main__':
    stockData = StockData('2010-01-01', '2023-04-14', 2)
    #stockData.updateStocks()
    #stockData.downloadData()


