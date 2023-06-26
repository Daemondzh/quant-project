import matplotlib.pyplot as plt
import numpy as np
from torch.utils.data import DataLoader
from config import *

def loss_curve(loss_list):
    """Plotting Loss Curve."""
    # Add plotting functionality here.
    x=np.linspace(1,len(loss_list),len(loss_list))
    x=20*x
    plt.cla()  # 清除axes，即当前 figure 中的活动的axes，但其他axes保持不变。
    plt.clf()  # 清除当前 figure 的所有axes，但是不关闭这个 window，所以能继续复用于其他的 plot
    plt.plot(x,np.array(loss_list),label="train_loss")
    plt.ylabel("MSELoss")
    plt.xlabel("iteration")
    fig = plt.gcf()
    fig.savefig("train_loss.png",dpi=300)
    plt.show()

def contrast_lines(stock_test, predict_list, std_list, mean_list):
    """Plotting Prediction-Real Data Contrast Lines."""
    # Add plotting functionality here.
    real_list=[]
    prediction_list=[]
    dataloader=DataLoader(dataset=stock_test,batch_size=BATCH_SIZE,shuffle=False,drop_last=True)
    date=[]
    for i,(data,label) in enumerate(dataloader):
        for idx in range(BATCH_SIZE):
            real_list.append(np.array(label[idx]*std_list[0]+mean_list[0]))
            #real_list.append(np.array(label[idx]))
            date.append(data[idx][0])
    for item in predict_list:
        item=item.to("cpu")
        for idx in range(BATCH_SIZE):
            prediction_list.append(np.array(item[idx]*std_list[0]+mean_list[0]))
            #prediction_list.append(np.array((item[idx])))
    x=np.linspace(1,len(real_list),len(real_list))
    plt.cla()  # 清除axes，即当前 figure 中的活动的axes，但其他axes保持不变。
    plt.clf()  # 清除当前 figure 的所有axes，但是不关闭这个 window，所以能继续复用于其他的 plot
    plt.plot(x,np.array(real_list),label="real")
    plt.plot(x,np.array(prediction_list),label="prediction")
    plt.legend()
    plt.savefig("transformer_Pre.png",dpi=300)
    plt.show()