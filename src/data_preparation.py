import pandas as pd
from config import *

def data_wash(dataset, keep_time=False):
    """Data Cleaning: Either drop the rows with missing values or fill them with previous values."""
    if keep_time:
        dataset.fillna(axis=1, method='ffill')
    else:
        dataset.dropna()
    return dataset

def import_csv(stock_code):
    """Import data from csv and preprocess it."""
    file_path = DIRECTORY + stock_code
    df = pd.read_csv(file_path + '.csv')
    df = data_wash(df, keep_time=False)
    df.rename(columns={
            'Timestamp': 'Date', 'Bid Price': 'Open',
            'Offer Price': 'High', 'Bid Quantity': 'Low',
            'Offer Quantity': 'Close'}, inplace=True)
    df.set_index(df['Date'], inplace=True)
    return df

def prepare_data(stock_code):
    """Prepare training and test data."""
    data = import_csv(stock_code)
    data.drop(['Num'],axis=1,inplace = True)
    train_size=int(TRAIN_WEIGHT*(data.shape[0]))
    train_data=data[:train_size+SEQ_LEN]
    test_data=data[train_size-SEQ_LEN:]
    train_data.to_csv(TRAIN_DATA_PATH,sep=',',index=False,header=False)
    test_data.to_csv(TEST_DATA_PATH,sep=',',index=False,header=False)
    return data
