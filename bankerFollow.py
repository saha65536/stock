# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 19:09:14 2020

@author: 1234656
"""

import os
import pandas as pd# 导入DataFrame数据
import baostock as bs


class bankerFollow:
    
    def __init__(self,beg_date,end_date,anaMonth,checkMonth):
        self.beg_date = beg_date
        self.end_date = end_date
        self.anaMonth = anaMonth
        self.checkMonth = checkMonth
        
        self.arr_code = []
        self.arr_score = []
        self.arr_increaseRate = []
        
        self.check_code = []
        self.check_score = []
        self.check_profit = []
        
        #### 登陆系统 ####
        lg = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:'+lg.error_code)
        print('login respond  error_msg:'+lg.error_msg) 
        self.getList()  
        self.getStocks()
        self.analyse()
        self.checkResult()
        
        
    def getList(self):
        stocks = []
    
        # 获取中证500成分股
        rs = bs.query_zz500_stocks()
        print('query_zz500 error_code:'+rs.error_code)
        print('query_zz500  error_msg:'+rs.error_msg)    
        
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            stocks.append(rs.get_row_data())
            
        # 获取中证500成分股
        rs = bs.query_hs300_stocks()
        print('query_hs300 error_code:'+rs.error_code)
        print('query_hs300  error_msg:'+rs.error_msg)    
        
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            stocks.append(rs.get_row_data())
            
        result = pd.DataFrame(stocks, columns=rs.fields)
        # 结果集输出到csv文件
        
        self.makeDIR('./data')
        result.to_csv('data/'+ 'stockList.csv', index=False) 
        
    def makeDIR(self,dirName):
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        
    #获取list中每个股票数据
    def getStocks(self):
        dfall = pd.read_csv('data/'+ 'stockList.csv')
        for i in range(0,len(dfall)):
            print('begin read :' + str(i) + ' '+ dfall.iloc[i]['code']+ ' '+ dfall.iloc[i]['code_name'])
            self.read_onestock(dfall.iloc[i]['code'])
            
    #读取一只股票的数据    
    def read_onestock(self,stock_code):    
        
        if os.path.isfile('data/'+ stock_code + '.csv'):
            return
        
        #### 获取沪深A股历史K线数据 ####
        # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
        # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
        # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
        rs = bs.query_history_k_data_plus(stock_code,
            "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
            start_date=self.beg_date, end_date=self.end_date,
            frequency="d", adjustflag="2")
        
        #### 打印结果集 ####
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        
        #### 结果集输出到csv文件 ####   
        result.to_csv('data/'+ stock_code + '.csv', index=False)  
       
    #模型分析
    def analyse(self):
        dfall = pd.read_csv('data/'+ 'stockList.csv')
        self.makeDIR('./result')
        for i in range(0,len(dfall)):
            print('begin Analyse :' + str(i) + ' '+ dfall.iloc[i]['code']+ ' '+ dfall.iloc[i]['code_name'])
            self.modelAnalyse(dfall.iloc[i]['code'],dfall.iloc[i]['code_name'])
            
        self.exportAnaResult()
    #分析每一只股票
    def modelAnalyse(self,stock_code,stock_name):
    	# 导入股票数据
        df = pd.read_csv('data/'+ stock_code + '.csv')
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
        
        
        #判断第二天最高点与第一天收盘价的比较结果     
        score = 0
        increaseRate = 0.0
        for i in range(1,len(df)):
            if not df.iloc[i]['od'].startswith(self.anaMonth) :
                break
            j = i - 1
            if df.iloc[i]['High'] > df.iloc[j]['Close']:
                score = score + 1
                increaseRate = increaseRate + (df.iloc[i]['High']-df.iloc[j]['Close'])/df.iloc[j]['Close'] * 100
        
        if score > 0:
            self.arr_code.append(stock_code)
            self.arr_score.append(score)
            self.arr_increaseRate.append(increaseRate/score)
            
    #输出分析结果
    def exportAnaResult(self):
        df = pd.DataFrame({'code':self.arr_code,'score':self.arr_score,'increaseRate':self.arr_increaseRate})

        self.makeDIR('./result')        
        df.sort_values(by= "score",ascending = False,inplace = True)
        df.to_csv('result/result_'  + self.anaMonth + '.csv' ,index=False,sep=',')        
        
    def checkResult(self):
        dfResult = pd.read_csv('result/result_'  + self.anaMonth + '.csv')
        self.makeDIR('./result')
        for i in range(0,21):
            print('check :' + str(i) + ' '+ dfResult.iloc[i]['code'])
            self.checkOneStock(dfResult.iloc[i]['code'])
            
        self.exportCheckResult()
    
    def checkOneStock(self,stock_code):
        # 导入股票数据
        df = pd.read_csv('data/'+ stock_code + '.csv')
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
        
        
        cost = 0.0
        profit = 0.0
        score = 0
        for i in range(1,len(df) - 1):
            if not df.iloc[i]['od'].startswith(self.checkMonth) :
                continue
            
            j = i + 1
            if cost < 0.1:
                cost = df.iloc[i]['Close']
                
            if df.iloc[j]['High'] > df.iloc[i]['Close']:
                score = score + 1
                
            if df.iloc[j]['High'] / df.iloc[i]['Close'] > 1.005:
                profit = profit + df.iloc[i]['Close'] * 0.005
            else:
                profit = profit + df.iloc[j]['Close'] -  df.iloc[i]['Close']
        
        self.check_code.append(stock_code)
        self.check_profit.append(profit/cost * 100)
        self.check_score.append(score)
        
     #输出分析结果
    def exportCheckResult(self):
        df = pd.DataFrame({'code':self.check_code,'profit':self.check_profit,'score':self.check_score})

        df.to_csv('result/check_' + self.checkMonth + '.csv',index=False,sep=',')  
        
         
        
if __name__ == '__main__':
    bankerFollow('2020-09-01','2020-10-31','2020-09','2020-10')