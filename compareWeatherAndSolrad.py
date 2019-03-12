import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

#SOLRAD -----------------
def readSolradDat (filename):
    print 'Reading ' + filename

    #Opens the file
    file = open(filename, 'r')

    #Reads the file
    raw_file_contents = file.read()

    #Splits the contents of the file by spaces
    split_file_contents = raw_file_contents.split(" ")

    cleaned_file_contents = []

    #Removes the empty items in the array
    for item in split_file_contents:
        if item != '':
            cleaned_file_contents.append(item)

    offset = 7
    row = 0
    rowLength = 22
    column = 0

    ordered_row = [];
    ordered_file_contents = [];

    for i in range(0, len(cleaned_file_contents)-8):
        row = i % rowLength
        item = float(cleaned_file_contents[i+offset])

        if(item<-100):
            item = -100

        ordered_row.append(item)

        #print(row, column, item)

        if(row == rowLength-1):
            column +=1

            timeStamp = datetime(int(ordered_row[0]),int(ordered_row[2]),int(ordered_row[3]),int(ordered_row[4]),int(ordered_row[5]))
            ordered_row.append(timeStamp)

            ordered_file_contents.append(ordered_row)
            ordered_row = []

    ordered_file_contents = np.array(ordered_file_contents)

    #Closes file
    file.close()

    return ordered_file_contents

solradData = np.array(readSolradDat('solrad_data\\hnx19057.dat'))
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19058.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19059.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19060.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19061.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19062.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19063.dat'),axis = 0)


#The weather channel ---------------------
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
    cloudPercentage = float(hour[0][6].replace('%',''))
    timeStamp = datetime.strptime(hour[0][1], '%Y-%m-%d %H:%M:%S.%f')

    cloudy_array.append([timeStamp, cloudPercentage])
cloudy_array = np.array(cloudy_array)

plt.plot(solradData[:,22], solradData[:,10], label = 'Direct')
#plt.plot(solradData[:,22], solradData[:,12], label = 'Diffuse')

plt.plot(cloudy_array[:,0],cloudy_array[:,1]*3)

plt.legend(loc = 'upper left')
plt.ylabel('Watts m^-2')
plt.xlabel('Time')
plt.show()
