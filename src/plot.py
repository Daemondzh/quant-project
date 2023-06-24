import pandas as pd
import matplotlib.pyplot as plt
import re

# Initialize lists for storing data
timestamps = []
bid_prices = []
offer_prices = []
bid_qty = []
offer_qty = []

with open('/workspaces/quant-project/log', 'r') as file:
    lines = file.readlines()
    fake_time = True
    for i, line in enumerate(lines):
        # Find timestamp
        if "Order book at" in line:
            if fake_time:
                fake_time = False
            else:
                timestamps.append(pd.to_datetime(time))
                bid_prices.append(bid_price)
                bid_qty.append(bid_order_qty)
                offer_prices.append(offer_price)
                offer_qty.append(offer_order_qty)
            
            time = re.findall("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)[0]
            
        # Find bid price and quantity
        if "Bid side:" in line:
            bid_line = re.findall("\d+\.\d+|\d+", lines[i+2])
            # print(bid_line)
            if not bid_line or fake_time:
                fake_time = True
                continue
            bid_price, bid_order_qty = float(bid_line[3]), float(bid_line[4])
            

        # Find offer price and quantity
        if "Offer side:" in line:
            offer_line = re.findall("\d+\.\d+|\d+", lines[i+2])
            if not offer_line or fake_time:
                fake_time = True
                continue
            offer_price, offer_order_qty = float(offer_line[3]), float(offer_line[4])
    
    if fake_time:
        fake_time = False
    else:
        timestamps.append(pd.to_datetime(time))
        bid_prices.append(bid_price)
        bid_qty.append(bid_order_qty)
        offer_prices.append(offer_price)
        offer_qty.append(offer_order_qty)

# Create a dataframe
data = {'Timestamp': timestamps, 
        'Bid Price': bid_prices, 
        'Offer Price': offer_prices, 
        'Bid Quantity': bid_qty, 
        'Offer Quantity': offer_qty}
df = pd.DataFrame(data)

df.to_csv('00069.csv')

# Set Timestamp as index
df = df.set_index('Timestamp')

# Plot the data
plt.figure(figsize=[15,10])
plt.grid(True)
plt.plot(df['Bid Price'], label='Bid Price', linewidth=2, markersize=12)
plt.plot(df['Offer Price'], label='Offer Price', linewidth=2, markersize=12)
plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.title('Bid and Offer Prices Over Time', fontsize=20)
plt.legend(loc=2)
plt.savefig('plot.png')
plt.show()
