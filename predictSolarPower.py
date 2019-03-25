#The full thing, read data from noaa, parse it, load the model and predict the solar power

from joblib import load
from bs4 import BeautifulSoup
from requests import get
import datetime
import numpy as np

print('Enter the location of the area you want to predict the solar power for')

lat = raw_input('Latitude:')
lon = raw_input('Longitude:')


#Gets the current date
datetime_object = datetime.datetime.now()


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

print('Gathering weather data from: ' + area_description.text)

#Weather data
time_containers = xml_soup.data.findAll('start-valid-time')
temperature_containers = xml_soup.data.parameters.findAll('temperature')[2].findAll('value')
cloud_amount_containers = xml_soup.data.parameters.findAll('cloud-amount')[0].findAll('value')
wind_speed_containers = xml_soup.data.parameters.findAll('wind-speed')[0].findAll('value')
humidity_containers = xml_soup.data.parameters.findAll('humidity')[0].findAll('value')
probability_of_precipitation_containers = xml_soup.data.parameters.findAll('probability-of-precipitation')[0].findAll('value')

#------Getting content from the containers-----
weatherData = []
for index in range(0,len(time_containers)):
    time = time_containers[index].text
    temperature = temperature_containers[index].text
    cloud_amount = cloud_amount_containers[index].text
    wind_speed = wind_speed_containers[index].text
    humidity = humidity_containers[index].text
    probability_of_precipitation = probability_of_precipitation_containers[index].text

    weatherData.append([datetime_object, time,temperature,cloud_amount,wind_speed,humidity,probability_of_precipitation])

weatherData = np.array(weatherData)

print(weatherData)
