import numpy as np
from sklearn.preprocessing import MinMaxScaler

# 选取价格作为预测目标，这里我们选取最优价格
data = df['price'].values.reshape(-1, 1)

# 使用MinMaxScaler将数据归一化到0-1之间
scaler = MinMaxScaler(feature_range=(0, 1))
data = scaler.fit_transform(data)

# 分割数据集为训练集和测试集
train_size = int(len(data) * 0.7)
train, test = data[0:train_size,:], data[train_size:len(data),:]

# 构建滞后特征，这里滞后1秒，即前1秒的价格用于预测下一秒的价格
def create_dataset(dataset, look_back=1):
    X, Y = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), 0]
        X.append(a)
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

look_back = 1
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)

from keras.models import Sequential
from keras.layers import Dense, LSTM

# 将输入转化为[samples, time steps, features]
trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

# 创建并拟合LSTM网络
model = Sequential()
model.add(LSTM(4, input_shape=(1, look_back)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)

from sklearn.metrics import mean_squared_error, r2_score

# 进行预测
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)

# 将预测数据转换回原始尺度
trainPredict = scaler.inverse_transform(trainPredict)
trainY = scaler.inverse_transform([trainY])
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform([testY])

# 计算均方误差
trainScore = np.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = np.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))

# 计算r2分数
r2 = r2_score(testY[0], testPredict[:,0])
print('R2 score: %.2f' % r2)