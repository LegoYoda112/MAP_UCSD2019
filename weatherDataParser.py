import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

csv_array = pd.read_csv('the_weather_channel\\the_weather_channel.csv').as_matrix()

ordered_hourly = []
hourly_forecast = []

hours_per_forecast = 16

for i in range(0,len(csv_array)-1):
    if((i+1) % hours_per_forecast == 0):
        ordered_hourly.append(np.array(hourly_forecast))
        hourly_forecast = []

    hourly_forecast.append(csv_array[i])

ordered_hourly = np.array(ordered_hourly)

cloudy_array = []
for hour in ordered_hourly:
    cloudPercentage = float(hour[0][5].replace('%',''))
    timeStamp = datetime.strptime(hour[0][1], '%Y-%m-%d %H:%M:%S.%f')

    cloudy_array.append([timeStamp, cloudPercentage])
cloudy_array = np.array(cloudy_array)

hourly_offset = 1
forecast_cloudy_array = []
for hour in ordered_hourly:
    cloudPercentage = float(hour[hourly_offset][5].replace('%',''))
    timeStamp = datetime.strptime(hour[hourly_offset][1], '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=hourly_offset)

    forecast_cloudy_array.append([timeStamp, cloudPercentage])
forecast_cloudy_array = np.array(forecast_cloudy_array)


plt.plot(cloudy_array[:,0],cloudy_array[:,1])
plt.plot(forecast_cloudy_array[:,0],forecast_cloudy_array[:,1])
plt.show()
