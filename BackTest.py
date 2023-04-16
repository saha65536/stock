import pandas as pd
import sqlite3

"""
写股票策略测试函数，根据提供的日期test_date和dataframe数据，进行如下测试：
如果test_date后第五天的收盘价(close)在test_date当天收盘价的[90,105]区间则在test_date后第五天以收盘价买入，
连续持股20天计算收益率，如果中间收益率超过20%则卖掉，如果低于-8%则卖掉，否则在持股后20天卖掉，输出每次策略的收益率
"""

def insert_into_table(insertArr):
    conn = sqlite3.connect('D:/sqlite/data/stocks_db.db')
    # 创建一个游标对象
    cur = conn.cursor()

    # 插入一行数据
    cur.execute("INSERT INTO stock_returns (code, buy_date, buy_price, sell_date, sell_price, return_rate) VALUES (?, ?, ?, ?, ?, ?)"
                , insertArr)

    # 提交事务并关闭连接
    conn.commit()
    conn.close()

def stock_strategy_test(test_date, df):
    # 首先找到test_date对应的索引
    test_index = df[df['date'] == test_date].index[0]
    
    # 找到第五天的索引
    buy_index = test_index + 5
    
    # 检查第五天的收盘价是否在指定区间内
    test_day_close = df.loc[test_index, 'close']
    buy_day_close = df.loc[buy_index, 'close']
    
    if 0.9 * test_day_close <= buy_day_close <= 1.05 * test_day_close:
        # 满足条件，以第五天的收盘价买入
        buy_price = buy_day_close
        
        # 初始化收益率为0
        return_rate = 0
        
        for i in range(buy_index + 1, buy_index + 21):
            # 当前收盘价
            current_close = df.loc[i, 'close']
            
            # 计算收益率
            current_return_rate = (current_close - buy_price) / buy_price * 100
            
            # 如果收益率超过20%，卖掉
            if current_return_rate > 20:
                return_rate = current_return_rate
                insertArr = (df['code'].iloc[1] ,df.loc[buy_index, 'date'] ,buy_price
                             ,df.loc[buy_index + i, 'date'], current_close, return_rate)                
                break
            
            # 如果收益率低于-8%，卖掉
            if current_return_rate < -8:
                return_rate = current_return_rate
                insertArr = (df['code'].iloc[1] ,df.loc[buy_index, 'date'] ,buy_price
                             ,df.loc[buy_index + i, 'date'], current_close, return_rate)  
                break
                
        # 如果20天内没有卖掉，则以第20天的收盘价卖掉
        if return_rate == 0:
            sell_close = df.loc[buy_index + 20, 'close']
            return_rate = (sell_close - buy_price) / buy_price * 100
            insertArr = (df['code'].iloc[1] ,df.loc[buy_index, 'date'] ,buy_price
                             ,df.loc[buy_index + 20, 'date'], sell_close, return_rate)  
            
        insert_into_table(insertArr)
        return return_rate
    else:
        return 0


