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
    cur.execute("INSERT INTO stock_returns (code, buy_date, buy_price, sell_date, sell_price, return_rate,backtest_strategy_id ) VALUES (?, ?, ?, ?, ?, ?, ?)"
                , insertArr)

    # 提交事务并关闭连接
    conn.commit()
    conn.close()

def stock_strategy_test(test_date, df):
    test_index = df[df['date'] == test_date].index[0]
    buy_index = test_index + 5
    
    test_day_close = df.loc[test_index, 'close']
    buy_day_close = df.loc[buy_index, 'close']
    
    if 0.9 * test_day_close <= buy_day_close <= 1.05 * test_day_close:
        buy_price = buy_day_close
        
        return_rate = 0
        additional_purchase = False
        investment_weight = 0.5
        
        for i in range(buy_index + 1, buy_index + 21):
            current_close = df.loc[i, 'close']
            current_return_rate = (current_close - buy_price) / buy_price * investment_weight * 100
            
            # 首次出现大于-8的亏损率，购买剩余的50%资金
            if not additional_purchase and current_return_rate > -8:
                additional_purchase = True
                investment_weight = 1  # 更新投资权重
                current_return_rate = (current_close - buy_price) / buy_price * investment_weight * 100
            
            # 如果收益率超过20%，卖掉
            if current_return_rate > 20:
                return_rate = current_return_rate
                insertArr = [df['code'].iloc[1], df.loc[buy_index, 'date'], buy_price,
                             df.loc[i, 'date'], current_close, return_rate]               
                break
            
            # 如果收益率低于-8%，卖掉
            if current_return_rate < -8:
                return_rate = current_return_rate
                insertArr = [df['code'].iloc[1], df.loc[buy_index, 'date'], buy_price,
                             df.loc[i, 'date'], current_close, return_rate]  
                break
                
        # 如果20天内没有卖掉，则以第20天的收盘价卖掉
        if return_rate == 0:
            sell_close = df.loc[buy_index + 20, 'close']
            return_rate = (sell_close - buy_price) / buy_price * investment_weight * 100
            insertArr = [df['code'].iloc[1], df.loc[buy_index, 'date'], buy_price,
                         df.loc[buy_index + 20, 'date'], sell_close, return_rate] 
            
        insertArr.append(2)    
        insert_tuple = tuple(insertArr)    
        insert_into_table(insert_tuple)
        return return_rate
    else:
        return 0





