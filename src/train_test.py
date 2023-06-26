import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader
from models import Stock_Data, TransAm
from config import *

def train(model, optimizer, device, epoch, stock_train, criterion, loss_list, iteration):
    """Training Function."""
    # Add training loop here.
    model.train()
    dataloader=DataLoader(dataset=stock_train,batch_size=BATCH_SIZE,shuffle=False,drop_last=True)
    for i,(data,label) in enumerate(dataloader):
        # print("data_size: ", data.size)
        iteration=iteration+1
        data,label = data.to(device),label.to(device)
        optimizer.zero_grad()
        output=model.forward(data)
        loss=criterion(output,label)
        loss.backward()
        optimizer.step()
        if i%20==0:
            loss_list.append(loss.item())
            print("epoch=",epoch,"iteration=",iteration,"loss=",loss.item())
        if epoch%EPOCH==0:
            torch.save(model.state_dict,SAVE_PATH+str(epoch)+"_Model.pkl")
            torch.save(optimizer.state_dict,SAVE_PATH+str(epoch)+"_Optimizer.pkl")

def test(model, optimizer, device, stock_test, criterion, accuracy_list, predict_list):
    """Testing Function."""
    # Add testing loop here.
    model.eval()
    dataloader=DataLoader(dataset=stock_test,batch_size=BATCH_SIZE,shuffle=False,drop_last=True)
    for i,(data,label) in enumerate(dataloader):
        with torch.no_grad():
            data,label=data.to(device),label.to(device)
            optimizer.zero_grad()
            predict=model.forward(data)
            predict_list.append(predict)
            loss=criterion(predict,label)
            accuracy_fn=nn.MSELoss()
            accuracy=accuracy_fn(predict,label)
            accuracy_list.append(accuracy.item())
    print("test_data MSELoss:(pred-real)/real=",np.mean(accuracy_list))