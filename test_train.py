import pickle
import numpy as np
import os
from sklearn.svm import SVR
from sklearn import tree
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import KNeighborsRegressor
import gzip

if __name__ == '__main__':
    rawData = np.array([0,0,0,0,0,0])
    for i in range(0,200):
        filename = os.path.join(os.path.dirname(__file__), "test_log", "test%d.pickle"%i)
        with open(filename,'rb') as file:
            log = pickle.load(file)
            rawData = np.vstack((rawData,log))

    mask = [0,1,2,3,4]
    X = rawData[1:,mask]
    Y = rawData[1:,5]

    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.15, shuffle=True)
    print("Training now...")
    model = KNeighborsRegressor().fit(x_train, y_train)
    #model = tree.DecisionTreeRegressor().fit(x_train, y_train)
    #model = MLPRegressor(hidden_layer_sizes=(512,256,128,64,32,16), verbose=True, learning_rate="adaptive").fit(x_train, y_train)
    print("Predicting now...")
    predict = model.predict(x_test)
    print("Calculating rmse...")
    rmse = np.sqrt(mean_squared_error(predict, y_test))
    print("方均根差 = %f"%rmse)

    with gzip.open(os.path.join(os.path.dirname(__file__), "save", 'model_test_s'), 'wb') as f:
        pickle.dump(model,f)

    """
    with open(os.path.join(os.path.dirname(__file__), "save", 'model_test'), 'wb') as f:
        pickle.dump(model, f)
    """