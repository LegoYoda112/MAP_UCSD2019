from joblib import load
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import pvlib as pv
import math

csv_array = pd.read_csv('noaa\\noaa.csv').as_matrix()

ordered_hourly = []
hourly_forecast = []
hour_forecast = []

hours_per_forecast = 168

#2019-02-26T15:00:00-08:00

for i in range(0,len(csv_array)-1):
    if((i+1) % hours_per_forecast == 0):
        ordered_hourly.append(np.array(hourly_forecast))
        hourly_forecast = []

    hour_forecast = csv_array[i]
    hour_forecast = np.append(hour_forecast, datetime.strptime(csv_array[i][2][:-6], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7) )

    hourly_forecast.append(hour_forecast)


ordered_hourly = np.array(ordered_hourly)

#Number of ours to look ahead in our data.
predicted_lookahead = 24*4

noaa_data_array = []
for hours in ordered_hourly:
    timeStamp = hours[predicted_lookahead][8]

    noaa_data_array.append([timeStamp, float(hours[predicted_lookahead][3]), float(hours[predicted_lookahead][4]), float(hours[predicted_lookahead][5]), float(hours[predicted_lookahead][6]), float(hours[predicted_lookahead][7])])
noaa_data_array = np.array(noaa_data_array)


# sets the location: latitude, longitude, and time zone
hnxloc = pv.location.Location(36.31357, -119.63164, 'US/Pacific')

#We create a times array that corrisponds to each entry in our trimmed arrays
times = pd.DatetimeIndex(noaa_data_array[:,0])

#Computes the clear sky (theoretical max) for each entry in the times array
cs = hnxloc.get_clearsky(times + timedelta(hours=0), model='ineichen', linke_turbidity=3)



predictInputs = []
for index in range(0, len(noaa_data_array)):
    predictInputs.append([noaa_data_array[index][2], noaa_data_array[index][3], noaa_data_array[index][4], noaa_data_array[index][5], cs['dhi'][index]])


#Reload the model
modelReloaded = load('MLPRegressor_model.joblib')
print('Model loaded')

plt.plot(times, (modelReloaded.predict(predictInputs)), label = 'Predicted using MLPRegressor and reloaded')

#plt.plot(times, cs['dhi']*(model.predict(predictInputs)), label = 'Predicted')
plt.legend(loc = 'upper left')
plt.show()
