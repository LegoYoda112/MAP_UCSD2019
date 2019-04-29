import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import pvlib as pv
import math
import os


data = pd.read_csv("savedData.csv")

print(data)


#Machine learning
X = []
y = []

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

#train_scaled = scaler.fit_transform(X_train)
#test_scaled = scaler.transform(X_test)

print("Test")

from sklearn.neural_network import MLPRegressor

model = MLPRegressor(max_iter = 1000, verbose = True, hidden_layer_sizes=(500,100,100), solver = 'lbfgs')

model.fit(X_train, y_train)

predictInputs = []
for index in range(0, len(noaa_data_array)):
    predictInputs.append([noaa_data_array[index][1],1 - noaa_data_array[index][2], noaa_data_array[index][3], noaa_data_array[index][4], noaa_data_array[index][5], cs['dni'][index]])

#plt.plot(times, cs['dhi']*(1-noaa_data_array[:,2]/100)*10, label = 'Predicted using just cloud %')

plt.plot(times, hourlySolradData[:,1], label = 'Actual')
plt.plot(times, (model.predict(predictInputs)), label = 'Predicted using MLPRegressor', linestyle='dashed', linewidth=1.5)

plt.legend(loc = 'upper left')
plt.show()

plt.scatter(hourlySolradData[:,1],model.predict(predictInputs))
plt.show()

from joblib import dump

dump(model, 'MLPRegressor_model.joblib')
print('Model has been dumped')
