import pandas as pd

# 1. 加载数据
stock_code = '000069'
df = pd.read_csv('/root/quant-project/sz_level3/000069/000069_20200110.csv.gz', compression='gzip')
df['transact_time'] = pd.to_datetime(df['transact_time'], format="%Y%m%d%H%M%S%f")
df['price'] = df['price'] / 10000  # 数据清洗，将价格恢复为真实值
df['order_qty'] = df['order_qty'] / 100  # 数据清洗，将订单数量恢复为真实值

df['stock_code'] = stock_code
# 时间点
times = ['2020-01-10 09:30:00.000', '2020-01-10 10:30:00.000', '2020-01-10 13:30:00.000']

for time in times:
    # 2. 按照指定时间筛选数据
    current_time = pd.to_datetime(time)
    df_time = df[df['transact_time'] <= current_time]
    
    # 3. 计算每个时间点的order book信息
    # 这里假设股票代码在'data.csv'文件中的列名为'stock_code'
    for stock_code in df_time['stock_code'].unique():
        df_stock = df_time[df_time['stock_code'] == stock_code]
        print("Stock Code:", stock_code, "Time:", current_time)
        
        # 买单
        df_buy = df_stock[df_stock['side'] == 1].sort_values(by='price', ascending=False)
        print("Buy Orders:")
        print(df_buy[['price', 'order_qty']].head(10))
        
        # 卖单
        df_sell = df_stock[df_stock['side'] == 2].sort_values(by='price')
        print("Sell Orders:")
        print(df_sell[['price', 'order_qty']].head(10))
