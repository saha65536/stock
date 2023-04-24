import pandas as pd
import baostock as bs
import os
import sqlite3
from datetime import datetime, timedelta

#股票数据类，下载数据并保存到文件
class StockData:
    CSV_TYPE = 1
    DB_TYPE = 2
    DBNAME = 'D:/sqlite/data/stocks_db.db'

    def __init__(self, beg_date, end_date, dataType, fhzType):
        lg = bs.login()
        print('login respond error_code:'+lg.error_code)
        print('login respond  error_msg:'+lg.error_msg) 
        self.__dataStoreDir__ = './data/'
        self.__resultStoreDir__ = './result/'
        self.__beg_date__ = beg_date
        self.__end_date__ = end_date
        self.__data_type__ = dataType 
        self.__fhz_type__ = fhzType
        if dataType == StockData.DB_TYPE:
            # 创建一个SQLite3连接
            try:
                self.conn = sqlite3.connect(StockData.DBNAME)
                #print("数据库连接成功")
            except sqlite3.Error as e:
                print("数据库连接失败：", e)

    def __del__(self):
        if self.__data_type__ == StockData.DB_TYPE:
            self.conn.close()
            #print("数据库已关闭")

    def downloadData(self):
        self.__getStocks__()

    def downloadOneStockData(self, code):
        self.__read_onestock__(code)
        self.conn.commit()
    
        
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
        if "d" == self.__fhz_type__:
            df.to_sql('stock_day_data', self.conn, if_exists='append', index=False,
                    dtype={'date': 'TEXT', 'code': 'TEXT', 'open': 'REAL', 'high': 'REAL',
                            'low': 'REAL', 'close': 'REAL', 'preclose': 'REAL', 'volume': 'INTEGER',
                            'amount': 'REAL', 'adjustflag': 'INTEGER', 'turn': 'REAL', 'tradestatus': 'INTEGER',
                            'pctChg': 'REAL', 'isST': 'INTEGER'})
        elif "30" == self.__fhz_type__:
            df.to_sql('stock_30min_data', self.conn, if_exists='append', index=False,
                    dtype={'date': 'TEXT', 'time': 'TEXT', 'code': 'TEXT', 'open': 'REAL', 'high': 'REAL',
                 'low': 'REAL', 'close': 'REAL', 'volume': 'REAL', 'amount': 'REAL', 'adjustflag': 'INTEGER'})



    def shrink_date_range(self, min_date, max_date, beg_date, end_date):
        if max_date is not None and min_date is not None:
            # 情况1: beg_date和end_date都在现有数据范围内
            if beg_date >= min_date and end_date <= max_date:
                return None, None

            # 情况2: beg_date在现有数据范围内，end_date在现有数据范围外
            if beg_date >= min_date and beg_date <= max_date and end_date > max_date:
                beg_date = max_date
                beg_date = datetime.strptime(beg_date, '%Y-%m-%d')
                beg_date += timedelta(days=1)
                beg_date = beg_date.strftime('%Y-%m-%d')

            # 情况3: end_date在现有数据范围内，beg_date在现有数据范围外
            if end_date >= min_date and end_date <= max_date and beg_date < min_date:
                end_date = min_date
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                end_date -= timedelta(days=1)
                end_date = end_date.strftime('%Y-%m-%d')

        return beg_date, end_date

    
    #读取一只股票的数据    
    def __read_onestock__(self, stock_code):    
        
        if os.path.isfile('data/'+ stock_code + '.csv'):
            return      
        
        # Create a cursor object to interact with the database
        cursor = self.conn.cursor()

        # Execute the SELECT query
        cursor.execute("SELECT min(date),max(date) from stock_day_data where code ='" + stock_code + "'")

        # Fetch the result of the query
        min_date, max_date = cursor.fetchone()

        # Close the cursor and the connection to the database
        cursor.close()

        beg_date = self.__beg_date__
        end_date = self.__end_date__

        beg_date, end_date = self.shrink_date_range(min_date, max_date, beg_date, end_date)

        if beg_date is None or beg_date > end_date:
            return

        
        # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
        # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
        if "d" == self.__fhz_type__:
            rs = bs.query_history_k_data_plus(stock_code,
                "date,code,open,high,low,close,preclose,volume"+
                ",amount,adjustflag,turn,tradestatus,pctChg,isST",
                start_date = beg_date, end_date = end_date,
                frequency=self.__fhz_type__, adjustflag="2")        
        else:
            rs = bs.query_history_k_data_plus(stock_code,
                "date,time,code,open,high,low,close,volume,amount,adjustflag",
                start_date = beg_date, end_date = end_date,
                frequency=self.__fhz_type__, adjustflag="2")
        
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
            self.__getList__()
            dfall = pd.read_csv('data/'+ 'stocks.csv')
            return dfall
        elif self.__data_type__ == StockData.DB_TYPE:
            df = pd.read_sql_query("select * from stocks_hs300 UNION ALL SELECT * from stocks_zz500", self.conn)
            return df    

    @staticmethod
    def getStockName(code):
        conn = sqlite3.connect(StockData.DBNAME)     
        cursor = conn.cursor()
        cursor.execute("select code_name from " 
                    + "(select code,code_name from stocks_hs300 UNION ALL SELECT code,code_name from stocks_zz500)"
                    + "where code = '" + code + "'")
        # Fetch the result of the query
        codeNm_tuple = cursor.fetchone()
        cursor.close()
        conn.close()
        if codeNm_tuple:
            return str(codeNm_tuple[0])
        else:
            return code
   
    
if __name__ == '__main__':
    stockData = StockData('2001-01-01', '2023-04-24', 2, 'd')
    #stockData.updateStocks()
    #stockData.downloadData()
    stockData.downloadOneStockData('sh.000001')


