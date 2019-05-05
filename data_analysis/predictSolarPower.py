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
from math import sin, cos, degrees, radians, acos

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def calcPVWatts(time, location, tilt, azimuth, DNI, DHI, temp, arrayRating):
    calcTime = time + timedelta(hours = 0)

    solarPosition = location.get_solarposition(calcTime)

    array_tilt_degrees = tilt
    array_azimuth_degrees = azimuth

    solar_zenith_degrees = solarPosition.zenith
    solar_azimuth_degrees = solarPosition.azimuth

    array_tilt_radians = radians(array_tilt_degrees)
    array_azimuth_radians = radians(array_azimuth_degrees)

    solar_zenith_radians = radians(solar_zenith_degrees)
    solar_azimuth_radians = radians(solar_azimuth_degrees)

    #Angle of incidence
    AOI_radians = acos(cos(solar_zenith_radians) * cos(array_tilt_radians)
                       + sin(solar_zenith_radians) * sin(array_tilt_radians)
                       *cos(solar_azimuth_radians - array_azimuth_radians))
    AOI_degrees = degrees(AOI_radians)

    POA_beam = DNI * cos(AOI_radians)
    POA_sky_diffuse = DHI * ((1+cos(array_tilt_radians))/2)
    POA_irradiance = POA_beam + POA_sky_diffuse

    pv_watts = pv.pvsystem.pvwatts_dc(g_poa_effective = POA_irradiance, temp_cell = temp, pdc0 = arrayRating, gamma_pdc = -0.003)
    return(pv_watts)

print('Enter the location of the area you want to predict the solar power for')

#lat = '32.9483'
#lon = '-117.12299'

lat = '32.8632543'
lon = '-117.2545537'
#lat = input('Lat: ')
#lon = input('Lon: ')

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
SolarLocation = pv.location.Location(float(lat), float(lon))

#We create a times array that corrisponds to each entry--
times = pd.DatetimeIndex(weatherData[:,1])

#Computes the clear sky (theoretical max) for each entry in the times array
cs = SolarLocation.get_clearsky(times, model='ineichen', linke_turbidity=3)
#

predictInputs = []

for index in range(0, len(weatherData)):
    predictInputs.append([weatherData[index][2],weatherData[index][3], weatherData[index][5], weatherData[index][6], cs['dni'][index]])

#Reload the model CHANGE THE FILE NAMES BEFORE UPLOADING
modelReloaded = load('MLPRegressor_model.joblib')
print('Model loaded')

MLP_predicted = np.array(modelReloaded.predict(predictInputs))

fileOutput = []

for index in range(0, len(MLP_predicted)):
    if(MLP_predicted[index][0] < 50):
        MLP_predicted[index][0] = 0

    time = weatherData[index][1]
    hoursOffset = 0
    tilt = 0
    azimuth = 0
    DNI = MLP_predicted[index][0]
    DHI = MLP_predicted[index][1]
    temp = (weatherData[index][2] - 32) * (5.0/9.0)

    pvwatts = calcPVWatts(time, SolarLocation, tilt, azimuth, DNI, DHI, temp, 8000)

    fileOutput.append([cs['dni'][index], MLP_predicted[index][1], MLP_predicted[index][0], pvwatts])

fileOutput = np.array(fileOutput)

#plt.plot(weatherData[:,1],weatherData[:,3], label = 'cloud-amount')
plt.plot(times, cs['dni'], label = 'Clear sky')
plt.plot(times, MLP_predicted[:,0], label = 'Predicted')
plt.plot(times, MLP_predicted[:,1], label = 'Predicted2')
plt.plot(times, fileOutput[:,3], label = 'Solar power')
plt.legend(loc = 'upper left')
plt.xlabel('Time')
plt.show()

file_name = 'predicted.csv'
predictedDF = pd.DataFrame(fileOutput, columns = ["Clear_Sky","DHI", "DNI", "pvwatts"])
predictedDF.to_csv(file_name, sep=',', encoding='utf-8', )
