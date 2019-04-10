#The full thing, read data from noaa, parse it, load the model and predict the solar power

from joblib import load
from bs4 import BeautifulSoup
from requests import get
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import pvlib as pv
import matplotlib.pyplot as plt

from matplotlib.pyplot import figure
figure(num=None, figsize=(15, 6), dpi=100)

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

print('Enter the location of the area you want to predict the solar power for')

lat = '32.9483'
lon = '-117.12299'

print('Downloading...')

#Gets the current date
datetime_object = datetime.now()

#------forecast.weather.gov------
url = 'https://forecast.weather.gov/MapClick.php?lat='+lat+'&lon='+lon+'&FcstType=digitalDWML'

#Pulls the html of the page
response = get(url)

#------Getting content from the containers-----
xml_soup = BeautifulSoup(response.text, 'html.parser')

#Area description
area_description = xml_soup.data.location.find('area-description')

if area_description is None:
    area_description = xml_soup.data.location.find('description')

#Weather data
time_containers = xml_soup.data.findAll('start-valid-time')
temperature_containers = xml_soup.data.parameters.findAll('temperature')[2].findAll('value')
cloud_amount_containers = xml_soup.data.parameters.findAll('cloud-amount')[0].findAll('value')
wind_speed_containers = xml_soup.data.parameters.findAll('wind-speed')[0].findAll('value')
humidity_containers = xml_soup.data.parameters.findAll('humidity')[0].findAll('value')
probability_of_precipitation_containers = xml_soup.data.parameters.findAll('probability-of-precipitation')[0].findAll('value')

def safeConvert (number):
    if number == '':
        number = 0
    if number == ' ':
        number = 0
    number = float(number)
    return number

#------Getting content from the containers-----
weatherData = []
for index in range(0,len(time_containers)):
    time = time_containers[index].text
    timezoneOffset = int(time[-5:-3])
    time = datetime.strptime(time[:-6], '%Y-%m-%dT%H:%M:%S') + timedelta(hours = timezoneOffset)
    temperature = safeConvert(temperature_containers[index].text)
    cloud_amount = safeConvert(cloud_amount_containers[index].text)
    wind_speed = safeConvert(wind_speed_containers[index].text)
    humidity = safeConvert(humidity_containers[index].text)
    probability_of_precipitation = safeConvert(probability_of_precipitation_containers[index].text)

    weatherData.append([datetime_object, time,temperature,cloud_amount,wind_speed,humidity,probability_of_precipitation])

weatherData = np.array(weatherData)

print('Gathered weather data for: ' + area_description.text)

print('Calculating the clear sky value')

# sets the location: latitude, longitude, and time zone
hnxloc = pv.location.Location(float(lat), float(lon))

#We create a times array that corrisponds to each entry--
times = pd.DatetimeIndex(weatherData[:,1])

#Computes the clear sky (theoretical max) for each entry in the times array
cs = hnxloc.get_clearsky(times, model='ineichen', linke_turbidity=3)
#
# plt.plot(weatherData[:,1],weatherData[:,3], label = 'cloud-amount')
# plt.plot(times, cs['dhi'], label = 'Clear sky')
# plt.legend(loc = 'upper left')
# plt.xlabel('Time')
# plt.show()

predictInputs = []

for index in range(0, len(weatherData)):
    predictInputs.append([weatherData[index][2],weatherData[index][3], weatherData[index][4], weatherData[index][5], weatherData[index][6], cs['dhi'][index]])

#Reload the model CHANGE THE FILE NAMES BEFORE UPLOADING
modelReloaded = load('MLPRegressor_model.joblib')
print('Model loaded')

MLP_predicted = modelReloaded.predict(predictInputs)

fileOutput = []

for index in range(0, len(MLP_predicted)):
    if(MLP_predicted[index] < 50):
        MLP_predicted[index] = 0

    fileOutput.append([MLP_predicted[index], cs['dhi'][index]])


file_name = 'forecastPage/predicted.csv'

print(fileOutput)

predictedDF = pd.DataFrame(fileOutput, columns = ["Solar power", "Clear sky"])
predictedDF.to_csv(file_name, sep='\t', encoding='utf-8', )

plt.style.use('seaborn-darkgrid')

plt.plot(times, MLP_predicted, label = 'Predicted using MLPRegressor')
plt.plot(times, cs['dhi']*(1-weatherData[:,3]/100)*10, label = 'Predicted using just cloudy %')
#
# #plt.plot(times, cs['dhi']*(model.predict(predictInputs)), label = 'Predicted')
plt.legend(loc = 'upper right')
plt.title('Solar power predictions for ' + area_description.text)
plt.ylabel('Watts m^-2')
plt.xlabel('Time')
plt.tight_layout(pad = 1)

# CHANGE THE FILE NAMES BEFORE UPLOADING
plt.savefig('forecastPage/sanDiegoForecast.png')
