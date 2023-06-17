import pandas as pd

# 定义函数构建订单簿
def create_order_book(df, timestamp):
    # 筛选出特定时间之前的所有交易数据
    df_prior = df[df['transact_time'] <= timestamp]

    # 筛选出下单、撤单和成交的记录
    orders = df_prior[(df_prior['order_type'] == '1') | (df_prior['order_type'] == '2') | (df_prior['order_type'] == 'U')]
    cancels = df_prior[df_prior['order_type'] == '4']
    trades = df_prior[df_prior['order_type'] == 'F']

    # 初始化订单簿
    order_book = pd.DataFrame(columns=['appl_seq_num', 'side', 'price', 'order_qty'])

    # 处理下单记录
    for _, order in orders.iterrows():
        lst = []
        for column in order_book.columns:
            lst.append(order[column])
        df_extended = pd.DataFrame([lst], columns=['appl_seq_num', 'side', 'price', 'order_qty'])
        order_book = pd.concat([order_book, df_extended], ignore_index=True)

    # 处理撤单记录
    for _, cancel in cancels.iterrows():
        if cancel['bid_appl_seq_num'] != 0:
            order_book = order_book[order_book['appl_seq_num'] != cancel['bid_appl_seq_num']]
        else:
            order_book = order_book[order_book['appl_seq_num'] != cancel['offer_appl_seq_num']]

    # 处理成交记录
    for _, trade in trades.iterrows():
        order_book.loc[order_book['appl_seq_num'] == trade['bid_appl_seq_num'], 'order_qty'] -= trade['order_qty']
        order_book.loc[order_book['appl_seq_num'] == trade['offer_appl_seq_num'], 'order_qty'] -= trade['order_qty']
        order_book = order_book[order_book['order_qty'] > 0]

    # 分别对买单和卖单进行排序
    bid_side = order_book[order_book['side'] == 1].sort_values(by='price', ascending=False)
    offer_side = order_book[order_book['side'] == 2].sort_values(by='price', ascending=True)

    # 取买卖两方向最优的10档数据
    bid_side = bid_side.head(10)
    offer_side = offer_side.head(10)

    return bid_side, offer_side

timestamps = ['2020-01-10 09:30:00', '2020-01-10 10:30:00', '2020-01-10 13:30:00']

df = pd.read_csv('/root/quant-project/sz_level3/000069/000069_20200110.csv.gz', compression='gzip')
df['transact_time'] = pd.to_datetime(df['transact_time'], format="%Y%m%d%H%M%S%f")
df['price'] = df['price'] / 10000  # 数据清洗，将价格恢复为真实值
df['order_qty'] = df['order_qty'] / 100  # 数据清洗，将订单数量恢复为真实值
stock_code = '000069'
df['stock_code'] = stock_code

for timestamp in timestamps:
    current_time = pd.to_datetime(timestamp)
    bid_side, offer_side = create_order_book(df, current_time)
    print("Order book at", timestamp)
    print("Bid side:")
    print(bid_side)
    print("Offer side:")
    print(offer_side)