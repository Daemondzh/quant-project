import torch
import torch.nn as nn
import numpy as np
import math
from torch.utils.data import Dataset
from config import *

class Stock_Data(Dataset):
    """Class for Stock Data."""
    # Add rest of the functionality here.
    def __init__(self, mean_list, std_list, train=True):
        if train==True:
            train_path=TRAIN_DATA_PATH
            with open(train_path) as f:
                self.data = np.genfromtxt(f,delimiter = ",")
                #可以注释
                #addi=np.zeros((self.data.shape[0],1))
                #self.data=np.concatenate((self.data,addi),axis=1)
                self.data=self.data[:,1:5]
            self.label=torch.rand(self.data.shape[0]-SEQ_LEN,1)
            for i in range(len(self.data[0])):
                mean_list.append(np.mean(self.data[:,i]))
                std_list.append(np.std(self.data[:,i]))
                self.data[:,i]=(self.data[:,i]-np.mean(self.data[:,i]))/(np.std(self.data[:,i])+1e-8)
            self.value=torch.rand(self.data.shape[0]-SEQ_LEN,SEQ_LEN,self.data.shape[1])
            for i in range(self.data.shape[0]-SEQ_LEN):
                self.value[i,:,:]=torch.from_numpy(self.data[i:i+SEQ_LEN,:].reshape(SEQ_LEN,self.data.shape[1]))
                self.label[i,:]=self.data[i+SEQ_LEN,0]
            self.data=self.value
        else:
            test_path=TEST_DATA_PATH
            with open(test_path) as f:
                self.data = np.genfromtxt(f,delimiter = ",")
                #addi=np.zeros((self.data.shape[0],1))
                #self.data=np.concatenate((self.data,addi),axis=1)
                self.data=self.data[:,1:5]
            self.label=torch.rand(self.data.shape[0]-SEQ_LEN,1)
            for i in range(len(self.data[0])):
                self.data[:,i]=(self.data[:,i]-mean_list[i])/(std_list[i]+1e-8)
            self.value=torch.rand(self.data.shape[0]-SEQ_LEN,SEQ_LEN,self.data.shape[1])
            for i in range(self.data.shape[0]-SEQ_LEN):
                self.value[i,:,:]=torch.from_numpy(self.data[i:i+SEQ_LEN,:].reshape(SEQ_LEN,self.data.shape[1]))
                self.label[i,:]=self.data[i+SEQ_LEN,0]
            self.data=self.value
    def __getitem__(self,index):
        return self.data[index],self.label[index]
    def __len__(self):
        return len(self.data[:,0])
    
class PositionalEncoding(nn.Module):
    """Class for Positional Encoding."""
    # Add rest of the functionality here.
    def __init__(self,d_model,max_len=SEQ_LEN):
        super(PositionalEncoding,self).__init__()
        #序列长度，dimension d_model
        pe=torch.zeros(max_len,d_model)
        position=torch.arange(0,max_len,dtype=torch.float).unsqueeze(1)
        div_term=torch.exp(torch.arange(0,d_model,2).float()*(-math.log(10000.0)/d_model))
        pe[:,0::2]=torch.sin(position*div_term)
        pe[:,1::2]=torch.cos(position*div_term)
        pe=pe.unsqueeze(0).transpose(0,1)
        self.register_buffer('pe',pe)

    def forward(self,x):
        return x+self.pe[:x.size(0),:]

class TransAm(nn.Module):
    """Class for TransAm Model."""
    # Add rest of the functionality here.
    def __init__(self,feature_size=4,num_layers=6,dropout=0.1):
        super(TransAm,self).__init__()
        self.model_type='Transformer'
        self.src_mask=None
        self.pos_encoder=PositionalEncoding(feature_size)
        self.encoder_layer=nn.TransformerEncoderLayer(d_model=feature_size,nhead=4,dropout=dropout)
        self.transformer_encoder=nn.TransformerEncoder(self.encoder_layer,num_layers=num_layers)
        #全连接层代替decoder
        self.decoder=nn.Linear(feature_size,1)
        self.linear1=nn.Linear(SEQ_LEN,1)
        self.init_weights()
        self.src_key_padding_mask=None

    def init_weights(self):
        initrange=0.1
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange,initrange)

    def forward(self,src,seq_len=SEQ_LEN):
        src=self.pos_encoder(src)
        #print(src)
        #print(self.src_mask)
        #print(self.src_key_padding_mask)
        #output=self.transformer_encoder(src,self.src_mask,self.src_key_padding_mask)
        output=self.transformer_encoder(src)
        output=self.decoder(output)
        output=np.squeeze(output)
        output=self.linear1(output)
        return output