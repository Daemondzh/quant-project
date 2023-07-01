import torch
import torch.nn as nn
import os
import torch.optim as optim
from data_preparation import prepare_data
from models import Stock_Data, TransAm
from train_test import train, test
from visualization import loss_curve, contrast_lines
from config import *

def main():
    # Add main execution logic here.

    #model=LSTM(dimension=4)
    #save_path=lstm_path
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model=TransAm(feature_size=4)

    model=model.to(device)
    criterion=nn.MSELoss()

    #if os.path.exists("./model_lstm/LSTM_"+str(EPOCH)+"_Model.pkl"):
    #    model.load_state_dict(torch.load("./model_lstm/epoch_"+str(EPOCH)+"_Model.pkl"))
    #optimizer=optim.Adam(model.parameters(),lr=LEARNING_RATE)
    #if os.path.exists("./model_lstm/LSTM_"+str(EPOCH)+"_Optimizer.pkl"):
    #    optimizer.load_state_dict(torch.load("./model_lstm/epoch_"+str(EPOCH)+"_Optimizer.pkl"))

    if os.path.exists("./model_transformer/TRANSFORMER_"+str(EPOCH)+"_Model.pkl"):
        model.load_state_dict(torch.load("./model_transformer/epoch_"+str(EPOCH)+"_Model.pkl"))
    optimizer=optim.Adam(model.parameters(),lr=LEARNING_RATE)
    if os.path.exists("./model_transformer/TRANSFORMER_"+str(EPOCH)+"_Optimizer.pkl"):
        optimizer.load_state_dict(torch.load("./model_transformer/epoch_"+str(EPOCH)+"_Optimizer.pkl"))
    
    data = prepare_data('00069')
    data.drop(['Date'],axis=1,inplace = True)
    mean_list = []
    std_list = []
    stock_train=Stock_Data(train=True, mean_list=mean_list, std_list=std_list)
    stock_test=Stock_Data(train=False, mean_list=mean_list, std_list=std_list)
    iteration=0
    loss_list=[]
    for epoch in range(1,EPOCH+1):
        predict_list=[]
        accuracy_list=[]
        train(model, optimizer, device, epoch, stock_train, criterion, loss_list, iteration)
        test(model, optimizer, device, stock_test, criterion, accuracy_list, predict_list)
    loss_curve(loss_list)
    contrast_lines(stock_test, predict_list, std_list, mean_list)

if __name__ == "__main__":
    main()