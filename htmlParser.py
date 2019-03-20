from bs4 import BeautifulSoup
import urllib2
from requests import get
import numpy as np
import pandas as pd
import datetime
import time
import lxml
import matplotlib.pyplot as plt
import os

print('Running...')



#Gets the current date
datetime_object = datetime.datetime.now()
formattedTime = datetime_object.strftime('%m-%d-%Y_%H-%M')
print(datetime_object)

#------Weather.com------
url = 'https://weather.com/weather/hourbyhour/l/USCA0461:1:US'
#San Diego airport https://weather.com/weather/fhourbyhour/l/SAN:9:US
#San Diego https://weather.com/weather/hourbyhour/l/USCA0982:1:US

#Pulls the html of the page
response = get(url)
#print(response.text[:500])


#-----HTML Containers------
html_soup = BeautifulSoup(response.text, 'html.parser')

time_containers = html_soup.find_all('span', class_ = 'dsx-date')
day_containers = html_soup.find_all('div', class_ = 'hourly-date')
description_containers = html_soup.find_all('td', class_ = 'hidden-cell-sm description')
temp_containers = html_soup.find_all('td', class_ = 'temp')
precip_containers = html_soup.find_all('td', class_ = 'precip')
humidity_containers = html_soup.find_all('td', class_ = 'humidity')
wind_containers = html_soup.find_all('td', class_ = 'wind')

#------Getting content from the containers----
weatherData = []

firstDay = day_containers[0].text

for index in range(0,len(time_containers)):

    #Time and day
    time = time_containers[index].text
    day = day_containers[index].text

    if(day!=firstDay):
        dayOffset = 1
    else:
        dayOffset = 0

    valtime = datetime_object.strptime((day + time),  '%a%I:%M %p')

    valtime = valtime.replace(datetime_object.year, datetime_object.month,  datetime_object.day+dayOffset)

    description = description_containers[index].span.text
    temp = temp_containers[index].span.text
    precip = precip_containers[index].find_all('span')[2].text
    humidity = humidity_containers[index].span.span.text
    wind = wind_containers[index].span.text

    weatherData.append([datetime_object, valtime, description, temp, precip, humidity, wind])

weatherData = np.array(weatherData)

#----Saving the csv file----
weatherDataFrame = pd.DataFrame(weatherData, columns=['reftime','valtime', 'description', 'temp', 'precip', 'humidity', 'wind'])
file_name = '/home/thomasg/getForecast/the_weather_channel/the_weather_channel.csv'
weatherDataFrame.to_csv(file_name, encoding='utf-8', mode = 'a', header = False)
print('Saved to: ' + file_name)


#------forecast.weather.gov------
url = 'https://forecast.weather.gov/MapClick.php?lat=36.3272&lon=-119.6458&FcstType=digitalDWML'

#Pulls the html of the page
response = get(url)
#print(response.text[:500])


#------Getting content from the containers-----
xml_soup = BeautifulSoup(response.text, 'html.parser')

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
    probability_of_precipitation = int(probability_of_precipitation_containers[index].text)

    weatherData.append([datetime_object, time,temperature,cloud_amount,wind_speed,humidity,probability_of_precipitation])

weatherData = np.array(weatherData)


#----Saving the csv file----
weatherDataFrame = pd.DataFrame(weatherData, columns=['reftime','time','temp', 'cloud-amount', 'wind-speed', 'humidity','probability_of_precipitation'])
file_name = '/home/thomasg/getForecast/noaa/noaa.csv'
weatherDataFrame.to_csv(file_name, encoding='utf-8', mode = 'a', header = False)
print('Saved to: ' + file_name)

print('Finished')

r = get("https://maker.ifttt.com/trigger/test_event/with/key/cxq1vMIaL4dqv14BLCa1Yl")
