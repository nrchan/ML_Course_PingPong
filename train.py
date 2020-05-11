import pickle
import numpy as np
import os
from sklearn.svm import SVR
from sklearn import tree
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import KNeighborsRegressor

def getData(filename):
    log = pickle.load((open(filename, 'rb')))

    ball = []
    ball_speed = []
    blocker = []
    estimate = []

    for i in log:
        ball.append(i["ball"])
        ball_speed.append(i["ball_speed"])
        blocker.append(i["blocker"])
        estimate.append((i["esti_1P"], i["esti_2P"]))
    
    rawData = np.hstack((ball,ball_speed,blocker,estimate))
    return rawData

if __name__ == '__main__':
    filename = os.path.join(os.path.dirname(__file__), "data.pickle")
    rawData = getData(filename)

    mask = [0,1,2,3,4]
    X = rawData[:,mask]
    Y1 = rawData[:,6]
    Y2 = rawData[:,7]

    x1_train, x1_test, y1_train, y1_test = train_test_split(X, Y1, test_size=0.15, shuffle=True)
    print("Training now...")
    model1 = KNeighborsRegressor().fit(x1_train, y1_train)
    #model1 = tree.DecisionTreeRegressor().fit(x1_train, y1_train)
    #model1 = MLPRegressor(hidden_layer_sizes=(512,256,128,64,32,16), verbose=True, learning_rate="adaptive").fit(x1_train, y1_train)
    print("Predicting now...")
    predict1 = model1.predict(x1_test)
    print("Calculating rmse...")
    rmse = np.sqrt(mean_squared_error(predict1, y1_test))
    print("方均根差 = %f"%rmse)

    with open(os.path.join(os.path.dirname(__file__), "ml", "save", 'model1'), 'wb') as f:
        pickle.dump(model1, f)

    x2_train, x2_test, y2_train, y2_test = train_test_split(X, Y2, test_size=0.15, shuffle=True)
    print("Training now...")
    model2 = KNeighborsRegressor().fit(x2_train, y2_train)
    #model2 = tree.DecisionTreeRegressor().fit(x2_train, y2_train)
    #model2 = MLPRegressor(hidden_layer_sizes=(512,256,128,64,32,16), verbose=True, learning_rate="adaptive").fit(x2_train, y2_train)
    print("Predicting now...")
    predict2 = model2.predict(x2_test)
    print("Calculating rmse...")
    rmse = np.sqrt(mean_squared_error(predict2, y2_test))
    print("方均根差 = %f"%rmse)

    with open(os.path.join(os.path.dirname(__file__), "ml", "save", 'model2'), 'wb') as f:
        pickle.dump(model2, f)