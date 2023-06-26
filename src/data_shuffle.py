import pandas as pd
from datetime import datetime, timedelta
import os

def create_order_book(df, timestamps):
    timestamps = pd.to_datetime(timestamps)
    ts_index = 0

    # Initialize order book and dictionary to store order books for different timestamps
    order_book = pd.DataFrame(columns=['appl_seq_num', 'side', 'price', 'order_qty'])
    # bid_side = pd.DataFrame()
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

            bid_side = order_book[order_book['side'] == 1].groupby('price')['order_qty'].sum().reset_index().sort_values(by='price', ascending=False).head(10)
            offer_side = order_book[order_book['side'] == 2].groupby('price')['order_qty'].sum().reset_index().sort_values(by='price', ascending=True).head(10)
            order_books[timestamps[ts_index]] = (bid_side, offer_side)
            ts_index += 1

        if row['order_type'] == '2':  # New order
            new_order = pd.DataFrame([row[['appl_seq_num', 'side', 'price', 'order_qty']]])
            new_orders = pd.concat([new_orders, new_order], ignore_index=True)
        elif row['order_type'] == '1':
            new_order = pd.DataFrame([row[['appl_seq_num', 'side', 'price', 'order_qty']]])
            if row['side'] == 2:
                new_order['price'] = max(new_orders[new_orders['side'] == 1]['price'].max(), order_book[order_book['side'] == 1]['price'].max())
            else:
                new_order['price'] = min(new_orders[new_orders['side'] == 2]['price'].min(), order_book[order_book['side'] == 2]['price'].min())
            new_orders = pd.concat([new_orders, new_order], ignore_index=True)
        elif row['order_type'] == 'U':
            new_order = pd.DataFrame([row[['appl_seq_num', 'side', 'price', 'order_qty']]])
            if row['side'] == 1:
                new_order['price'] = max(new_orders[new_orders['side'] == 1]['price'].max(), order_book[order_book['side'] == 1]['price'].max())
            else:
                new_order['price'] = min(new_orders[new_orders['side'] == 2]['price'].min(), order_book[order_book['side'] == 2]['price'].min())
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
        
        if ts_index == len(timestamps):
            break

    # If there are still timestamps left after looping through the dataframe, finalize the order books for those timestamps
    while ts_index < len(timestamps):
        # Concat new orders to the order book
        if not new_orders.empty:
            order_book = pd.concat([order_book, new_orders], ignore_index=True)
            new_orders = new_orders.iloc[0:0]  # Clear new_orders DataFrame

        bid_side = order_book[order_book['side'] == 1].sort_values(by='price', ascending=False).head(1)
        offer_side = order_book[order_book['side'] == 2].sort_values(by='price', ascending=True).head(1)
        order_books[timestamps[ts_index]] = (bid_side, offer_side)
        ts_index += 1

    return order_books

def data_generate(directory, stock_code):
    # Create date range
    date_range = pd.date_range(start="2020-01-23", end="2020-07-07")

    # Create an output file for the stock code
    output_file = open(stock_code + '.txt', 'w')

    for date in date_range:
    # Format date as a string in the form YYYY-MM-DD
        timestamps = []
        date_str = date.strftime("%Y%m%d")

        # Construct the full path of the file
        file_name = stock_code + "_" + date_str+ ".csv.gz"
        file_path = os.path.join(directory, file_name)

        # Check if a file with this name exists in the directory
        if os.path.isfile(file_path):
            do_flag = True
            # print("File '{file_name}' exists.")
        else:
            # print("File '{file_name}' does not exist.")
            continue

        time_0 = datetime.strptime("09:30:00", '%H:%M:%S').time()
        time_1 = datetime.strptime("11:30:00", '%H:%M:%S').time()
        start_time = datetime.combine(date, time_0)  # Specify your desired start time
        end_time = datetime.combine(date, time_1)  # Specify your desired end time

        # Define the time step as 3 seconds
        time_step = timedelta(seconds=3)

        # Calculate the total number of steps
        num_steps = int((end_time - start_time) / time_step) + 1

        # Generate and print timestamps
        current_time = start_time
        for _ in range(num_steps):
            timestamps.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
            current_time += time_step

        time_0 = datetime.strptime("13:00:00", '%H:%M:%S').time()
        time_1 = datetime.strptime("15:00:00", '%H:%M:%S').time()
        start_time = datetime.combine(date, time_0)  # Specify your desired start time
        end_time = datetime.combine(date, time_1)  # Specify your desired end time

        # Calculate the total number of steps
        num_steps = int((end_time - start_time) / time_step) + 1

        # Generate and print timestamps
        current_time = start_time
        for _ in range(num_steps):
            timestamps.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
            current_time += time_step

        df = pd.read_csv(file_path, compression='gzip')
        df['transact_time'] = pd.to_datetime(df['transact_time'], format="%Y%m%d%H%M%S%f")
        df['price'] = df['price'] / 10000  # Data cleaning, restore the price to its real value
        df['order_qty'] = df['order_qty'] / 100  # Data cleaning, restore the order quantity to its real value
        df['stock_code'] = stock_code

        order_books = create_order_book(df, timestamps)

        for timestamp, (bid_side, offer_side) in order_books.items():
            output_file.write("Order book at " + timestamp + "\n")
            output_file.write("Bid side:\n")
            output_file.write(bid_side + "\n")
            output_file.write("Offer side:\n")
            output_file.write(offer_side + "\n")

    # Close the output file when finished
    output_file.close()
    
# Set the directory where files are stored
directory = "/workspaces/quant-project/data/sz_level3/000069/"  # Current directory


for stock_code in  ['000069','000566','000876','002304','002841','002918']:
# Enumerate through each date in the range
    data_generate(directory, stock_code)
