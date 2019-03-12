import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    timeStamp = hour[0][1]

    cloudy_array.append([timeStamp, cloudPercentage])
cloudy_array = np.array(cloudy_array)

print(cloudy_array[:,0])

plt.plot(cloudy_array[:,1])
plt.show()
