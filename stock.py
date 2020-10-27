# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 11:24:53 2020

@author: saha
"""
import os
import mplfinance as mpf
import matplotlib as mpl# 用于设置曲线参数
from cycler import cycler# 用于定制线条颜色
import pandas as pd# 导入DataFrame数据
import baostock as bs
import matplotlib.pyplot as plt

import pandas_datareader.data as web
import datetime as dt



period = 40
arr_code=[]
arr_name=[]
arr_dt_before=[]
arr_dt_after=[]
arr_top_before=[]
arr_top_after=[]
beg_date='2020-06-01'
end_date=dt.datetime.now().strftime('%Y-%m-%d')

top_windows=11

def modelAnalyse(stock_code,stock_name):
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
    
    #获取成交量10日均线
    volMav = df.rolling(10,10).mean()
    df['volMav'] = volMav['Volume']

    #获取股票价格的局部峰值
    top = df.rolling(top_windows,top_windows,True).max()    
    df['topTmp'] = top['High']
    dfTmp = df.where(df['topTmp'] == df['High'],0)
    df['top'] = dfTmp['topTmp']
    
    isModel = False
    
    #判断成交量和价格背离
    for i in range(len(df) -period,len(df)):
        for j in range(i + 1, len(df)):
            if df.iloc[i]['top']!=0 and df.iloc[j]['top']!=0:
                if df.iloc[i]['top'] > df.iloc[j]['top'] and df.iloc[i]['volMav'] < df.iloc[j]['volMav']:
                    arr_code.append(stock_code)
                    arr_name.append(stock_name)
                    arr_dt_before.append(df.iloc[i]['od'])
                    arr_dt_after.append(df.iloc[j]['od'])
                    arr_top_before.append(df.iloc[i]['top'])
                    arr_top_after.append(df.iloc[j]['top'])

                    isModel = True
                else:
                    break
    
    #30日内有一个涨停
    dailyLimit = False
    stockRange = df['pctChg'][-30:]
    for oneRange in stockRange:
        if oneRange > 9.7:
            dailyLimit = True
            break
     
    if isModel and dailyLimit:
        draw(stock_code,df[-period:])

#画蜡烛图和交易量图
def draw(stock_code,df):        
    
    # 设置基本参数
    # type:绘制图形的类型，有candle, renko, ohlc, line等
    # 此处选择candle,即K线图
    # mav(moving average):均线类型,此处设置7,30,60日线
    # volume:布尔类型，设置是否显示成交量，默认False
    # title:设置标题
    # y_label:设置纵轴主标题
    # y_label_lower:设置成交量图一栏的标题
    # figratio:设置图形纵横比
    # figscale:设置图形尺寸(数值越大图像质量越高)
    kwargs = dict(
    	type='candle', 
    	mav=(10, 20, 30), 
    	volume=True, 
    	title='\nA_stock %s candle_line' % (stock_code),    
    	ylabel='OHLC Candles', 
    	ylabel_lower='Shares\nTraded Volume', 
    	figratio=(15, 10), 
    	figscale=5)
    
    # 设置marketcolors
    # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
    # down:与up相反，这样设置与国内K线颜色标准相符
    # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
    # wick:灯芯(上下影线)颜色
    # volume:成交量直方图的颜色
    # inherit:是否继承，选填
    mc = mpf.make_marketcolors(
    	up='red', 
    	down='green', 
    	edge='i', 
    	wick='i', 
    	volume='in', 
    	inherit=True)
    	
    # 设置图形风格
    # gridaxis:设置网格线位置
    # gridstyle:设置网格线线型
    # y_on_right:设置y轴位置是否在右
    s = mpf.make_mpf_style(
    	gridaxis='both', 
    	gridstyle='-.', 
    	y_on_right=False, 
    	marketcolors=mc)
    	
    # 设置均线颜色，配色表可见下图
    # 建议设置较深的颜色且与红色、绿色形成对比
    # 此处设置七条均线的颜色，也可应用默认设置
    mpl.rcParams['axes.prop_cycle'] = cycler(
        color=['dodgerblue', 'deeppink', 
        'navy', 'teal', 'maroon', 'darkorange', 
        'indigo'])
        
    # 设置线宽
    mpl.rcParams['lines.linewidth'] = .5
    
    add_plot = mpf.make_addplot(df['volMav'], panel='lower', color='r', secondary_y='auto')
    
    # 图形绘制
    # show_nontrading:是否显示非交易日，默认False
    # savefig:导出图片，填写文件名及后缀
    fileName = 'result/'+'%s %s_candle_line' % (stock_code, period) + '.jpg'
    if not os.path.exists(fileName): 
        mpf.plot(df, 
        	**kwargs, 
        	style=s, 
            addplot=add_plot,
        	show_nontrading=False,
        	savefig=fileName)
    
        plt.show()
    
def getRoeAvg(stock_code):
    profit_list = []
    rs_profit = bs.query_profit_data(stock_code,year=2020, quarter=2)
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_list.append(rs_profit.get_row_data())
        
    result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
    roeAvg = result_profit['roeAvg']
    if roeAvg[0] =='' :
        return False
    if float(roeAvg) > 0.2:
        print(roeAvg)
        return True
    return False
    

#读取一只股票的数据    
def read_onestock(stock_code):    
    
    if os.path.isfile('data/'+ stock_code + '.csv'):
        return
    
    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(stock_code,
        "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
        start_date=beg_date, end_date=end_date,
        frequency="d", adjustflag="2")
    
    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    
    #### 结果集输出到csv文件 ####   
    result.to_csv('data/'+ stock_code + '.csv', index=False)  
    
    
def exportResult():       
    
    #汇总最后筛选结果
    dataframe = pd.DataFrame({'code':arr_code,'name':arr_name,'dt_before':arr_dt_before
                              ,'top_before':arr_top_before,'dt_after':arr_dt_after
                              ,'top_after':arr_top_after})

    #将DataFrame存储为csv,index表示是否显示行名，default=True
    dataframe.to_csv('result/result.csv',index=False,sep=',')
    
def analyse():
    #模型分析
    dfall = pd.read_csv('data/'+ 'stocks.csv')
    makeDIR('./result')
    for i in range(0,len(dfall)):
        print('begin Analyse :' + str(i) + ' '+ dfall.iloc[i]['code']+ ' '+ dfall.iloc[i]['code_name'])
        modelAnalyse(dfall.iloc[i]['code'],dfall.iloc[i]['code_name'])
        
    
def getStocks():
    #获取每个股票数据
    dfall = pd.read_csv('data/'+ 'stocks.csv')
    for i in range(0,len(dfall)):
        print('begin read :' + str(i) + ' '+ dfall.iloc[i]['code']+ ' '+ dfall.iloc[i]['code_name'])
        read_onestock(dfall.iloc[i]['code'])
        
def makeDIR(dirName):
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    
    
    
def getList():
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
        
    result = pd.DataFrame(stocks, columns=rs.fields)
    # 结果集输出到csv文件
    
    makeDIR('./data')
    result.to_csv('data/'+ 'stocks.csv', index=False)
    
    
#主函数入口
#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg) 

#获取中证500清单
getList()
#获取中证500每个股票数据
getStocks()
#模型分析
analyse()
#导出分析结果
exportResult()

#### 登出系统 ####
bs.logout()



