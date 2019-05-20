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

#print(data)

#direct, temp, cloud_amount, wind_speed, humidity, probability_of_precipitation, clear_sky
# data['probability_of_precipitation']

unshapedX = np.array([data['temp'], data['cloud_amount'],data['wind_speed'], data['humidity'], data['probability_of_precipitation'], data['clear_sky']])
unshapedY = np.array([data["direct"], data["diffuse"]])
#Inputs and outputs
X = unshapedX.transpose(1,0)
y = unshapedY.transpose(1,0)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = MLPRegressor(max_iter = 200, verbose = True, hidden_layer_sizes=(100,50), solver = 'adam')

model.fit(X_train, y_train)

predictions = model.predict(X)

predictionsForError = []
measuredForError = []

for i in range(0, len(y)):
    if(y[i][0] > 100):
        measuredForError.append(y[i][0])
        predictionsForError.append(predictions[i][0])

measuredForError = np.array(measuredForError)
predictionsForError = np.array(predictionsForError)

plt.plot(measuredForError)
plt.plot(predictionsForError)
plt.show()

print(np.sum(abs((measuredForError[:]- predictionsForError[:]))/(len(measuredForError))))

plt.plot(data.index, y[:, 0], label = 'Actual Direct')
plt.plot(data.index, predictions[:, 0], label = 'Predicted Direct', linestyle='dashed', linewidth=1.5)
#plt.plot(data.index, (predictions[:, 0] - y[:, 0]), label = "Error")
plt.plot(data.index, y[:, 1], label = 'Actual Diffuse')
plt.plot(data.index, predictions[:, 1], label = 'Predicted Diffuse', linestyle='dashed', linewidth=1.5)
#plt.plot(data.index, X[:,4])

plt.tight_layout()
plt.legend(loc = 'upper left')
plt.show()

from joblib import dump

dump(model, 'MLPRegressor_model.joblib')
print('Model has been dumped')
