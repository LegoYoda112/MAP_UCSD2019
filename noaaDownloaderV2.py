from bs4 import BeautifulSoup
from requests import get
import numpy as np
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
import os

#Gets the current date
datetime_object = datetime.datetime.now()
formattedTime = datetime_object.strftime('%m-%d-%Y_%H-%M')
print(datetime_object)


def downloadNOAA(lat, lon, name):
    #------forecast.weather.gov------
    url = 'https://forecast.weather.gov/MapClick.php?lat=' + str(lat) + '&lon=' + str(lon) + '&FcstType=digitalDWML'

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
        probability_of_precipitation = probability_of_precipitation_containers[index].text

        weatherData.append([datetime_object, time,temperature,cloud_amount,wind_speed,humidity,probability_of_precipitation])

    weatherData = np.array(weatherData)


    #----Saving the csv file----
    weatherDataFrame = pd.DataFrame(weatherData, columns=['reftime','time','temp', 'cloud-amount', 'wind-speed', 'humidity','probability_of_precipitation'])
    file_name = 'noaa/noaa-' +name +'.csv'
    weatherDataFrame.to_csv(file_name, encoding='utf-8', mode = 'a', header = False)
    print('Saved to: ' + file_name)

    print('Finished')

#ABQ
downloadNOAA(35.03796, -106.62211, 'ABQ')
#BIS
downloadNOAA(46.77179, -100.75955, 'BIS')
#HNX
#downloadNOAA(36.31357, -119.63164, 'HNX')
#MSN
downloadNOAA(43.07250, -89.41133, 'MSN')
#ORT
downloadNOAA(35.96101, -84.28838, 'ORT')
#SLC
downloadNOAA(40.77220, -111.95495, 'SLC')
#SEA
downloadNOAA(47.68685, -122.25667, 'SEA')
#TLH
downloadNOAA(30.39675, -84.32955, 'TLH')
