import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

csv_array = pd.read_csv('noaa\\noaa-hnx.csv').as_matrix()

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
    hour_forecast = np.append(hour_forecast, datetime.strptime(csv_array[i][2][:-6], '%Y-%m-%dT%H:%M:%S'))

    hourly_forecast.append(hour_forecast)


ordered_hourly = np.array(ordered_hourly)

print(len(ordered_hourly))

print(ordered_hourly[0][0][3])

cloudy_array = []
for hours in ordered_hourly:
    cloudPercentage = float(hours[0][5])
    timeStamp = hours[0][8]

    cloudy_array.append([timeStamp, cloudPercentage])
cloudy_array = np.array(cloudy_array)


plt.plot(cloudy_array[:,0],cloudy_array[:,1])
plt.show()
