from bs4 import BeautifulSoup
import urllib2
from requests import get
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import time
import os


#------forecast.weather.gov------
datetime_object = datetime.datetime.now()
url = 'https://forecast.weather.gov/MapClick.php?lat=36.3272&lon=-119.6458'

print(datetime_object)

#Pulls the html of the page
response = get(url)

#------Getting content from the containers-----
html_soup = BeautifulSoup(response.text, 'html.parser')

text_containers = html_soup.find_all('div', class_ = 'col-sm-10 forecast-text')

textData = []

for index in range(0,len(text_containers)):
    text = text_containers[index].text
    reftime = datetime_object + timedelta(days=index)

    textData.append([datetime_object, reftime, text])

textData = np.array(textData)

#----Saving the csv file----
textDataFrame = pd.DataFrame(textData, columns=['reftime','time','text'])
#file_name = '/home/thomasg/getForecast/noaa/noaa.csv'
file_name = 'noaa/noaaText.csv'
textDataFrame.to_csv(file_name, encoding='utf-8', mode = 'a', header = False)
print('Saved to: ' + file_name)

#r = get("https://maker.ifttt.com/trigger/test_event/with/key/cxq1vMIaL4dqv14BLCa1Yl")
