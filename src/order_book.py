import pandas as pd

def create_order_book(df, timestamps):
    timestamps = sorted(pd.to_datetime(timestamps))
    ts_index = 0

    # Initialize order book and dictionary to store order books for different timestamps
    order_book = pd.DataFrame(columns=['appl_seq_num', 'side', 'price', 'order_qty'])
    new_orders = pd.DataFrame(columns=['appl_seq_num', 'side', 'price', 'order_qty'])
    order_books = {ts: None for ts in timestamps}

    # Loop through sorted dataframe
    for idx, row in df.iterrows():
        # If the timestamp of the current row is greater than the current timestamp in the list,
        # finalize the order book for the current timestamp, then move to the next timestamp
        while ts_index < len(timestamps) and row['transact_time'] > timestamps[ts_index]:
            # Concat new orders to the order book
            if not new_orders.empty:
                order_book = pd.concat([order_book, new_orders], ignore_index=True)
                new_orders = new_orders.iloc[0:0]  # Clear new_orders DataFrame

            bid_side = order_book[order_book['side'] == 1].sort_values(by='price', ascending=False).head(10)
            offer_side = order_book[order_book['side'] == 2].sort_values(by='price', ascending=True).head(10)
            order_books[timestamps[ts_index]] = (bid_side, offer_side)
            ts_index += 1

        if row['order_type'] == '2':  # New order
            new_order = pd.DataFrame([row[['appl_seq_num', 'side', 'price', 'order_qty']]])
            new_orders = pd.concat([new_orders, new_order], ignore_index=True)
        elif row['order_type'] == '1':
            new_order = pd.DataFrame([row[['appl_seq_num', 'side', 'price', 'order_qty']]])
            if row['side'] == 2:
                new_order['price'] = max(new_orders[new_orders['side'] == 1]['price'].max(), bid_side.iloc[0]['price'])
            else:
                new_order['price'] = min(new_orders[new_orders['side'] == 2]['price'].min(), offer_side.iloc[0]['price'])
            new_orders = pd.concat([new_orders, new_order], ignore_index=True)
        elif row['order_type'] == 'U':
            new_order = pd.DataFrame([row[['appl_seq_num', 'side', 'price', 'order_qty']]])
            if row['side'] == 1:
                new_order['price'] = max(new_orders[new_orders['side'] == 1]['price'].max(), bid_side.iloc[0]['price'])
            else:
                new_order['price'] = min(new_orders[new_orders['side'] == 2]['price'].min(), offer_side.iloc[0]['price'])
            new_orders = pd.concat([new_orders, new_order], ignore_index=True)
        elif row['order_type'] == '4':  # Cancel order
            if row['bid_appl_seq_num'] != 0:
                new_orders = new_orders[new_orders['appl_seq_num'] != row['bid_appl_seq_num']]
                order_book = order_book[order_book['appl_seq_num'] != row['bid_appl_seq_num']]
            if row['offer_appl_seq_num'] != 0:
                new_orders = new_orders[new_orders['appl_seq_num'] != row['offer_appl_seq_num']]
                order_book = order_book[order_book['appl_seq_num'] != row['offer_appl_seq_num']]
        elif row['order_type'] == 'F':  # Execute trade
            new_orders.loc[new_orders['appl_seq_num'] == row['bid_appl_seq_num'], 'order_qty'] -= row['order_qty']
            new_orders.loc[new_orders['appl_seq_num'] == row['offer_appl_seq_num'], 'order_qty'] -= row['order_qty']
            new_orders = new_orders[new_orders['order_qty'] > 0]
            order_book.loc[order_book['appl_seq_num'] == row['bid_appl_seq_num'], 'order_qty'] -= row['order_qty']
            order_book.loc[order_book['appl_seq_num'] == row['offer_appl_seq_num'], 'order_qty'] -= row['order_qty']
            order_book = order_book[order_book['order_qty'] > 0]

    # If there are still timestamps left after looping through the dataframe, finalize the order books for those timestamps
    while ts_index < len(timestamps):
        # Concat new orders to the order book
        if not new_orders.empty:
            order_book = pd.concat([order_book, new_orders], ignore_index=True)
            new_orders = new_orders.iloc[0:0]  # Clear new_orders DataFrame

        bid_side = order_book[order_book['side'] == 1].sort_values(by='price', ascending=False).head(10)
        offer_side = order_book[order_book['side'] == 2].sort_values(by='price', ascending=True).head(10)
        order_books[timestamps[ts_index]] = (bid_side, offer_side)
        ts_index += 1

    return order_books


timestamps = ['2020-01-10 09:30:00', '2020-01-10 10:30:00', '2020-01-10 13:30:00']
for stock_code in  ['000069','000566','000876','002304','002841','002918']:
    df = pd.read_csv('/workspaces/quant-project/data/sz_level3/'+stock_code+'/'+stock_code+'_20200110.csv.gz', compression='gzip')
    df['transact_time'] = pd.to_datetime(df['transact_time'], format="%Y%m%d%H%M%S%f")
    df['price'] = df['price'] / 10000  # Data cleaning, restore the price to its real value
    df['order_qty'] = df['order_qty'] / 100  # Data cleaning, restore the order quantity to its real value
    df['stock_code'] = stock_code

    order_books = create_order_book(df, timestamps)

    for timestamp, (bid_side, offer_side) in order_books.items():
        print('Stock Code:', stock_code)
        print("Order book at", timestamp)
        print("Bid side:")
        print(bid_side)
        print("Offer side:")
        print(offer_side)