import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import pvlib as pv

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

solradData = np.array(readSolradDat('solrad_data\\hnx19058.dat'))
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19059.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19060.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19061.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19062.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19063.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19064.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19065.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19066.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19067.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19068.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19069.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19070.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19071.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19072.dat'),axis = 0)
solradData = np.append(solradData, readSolradDat('solrad_data\\hnx19073.dat'),axis = 0)

hourlySolradData = []

for i in range(0, len(solradData)/60):
    hourOfSolradData = []
    timeStamp = solradData[(i*60)][22]
    for j in range(0, 60):
        direct = solradData[(i*60)+j][10]
        diffuse = solradData[(i*60)+j][12]
        hourOfSolradData.append(np.array([direct, diffuse]))
        #print(solradData[(i*60)+j][10])
        #print(solradData[(i*60)+j][5])
        #print((i*60)+j)

    hourOfSolradData = np.array(hourOfSolradData)
    directAvg = np.average(hourOfSolradData[:,0])
    directStd = np.std(hourOfSolradData[:,0])
    diffuseAvg = np.average(hourOfSolradData[:,1])
    diffuseStd = np.std(hourOfSolradData[:,1])

    hourlySolradData.append([timeStamp, directAvg, directStd, diffuseAvg, diffuseStd])

    #timeStamp = 0

hourlySolradData = np.array(hourlySolradData)

#NOAA ---------------------
csv_array = pd.read_csv('noaa\\noaa.csv').as_matrix()

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
    hour_forecast = np.append(hour_forecast, datetime.strptime(csv_array[i][2][:-6], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7) )

    hourly_forecast.append(hour_forecast)


ordered_hourly = np.array(ordered_hourly)

#hours
predicted_lookahead = 24*4

noaa_data_array = []
for hours in ordered_hourly:
    timeStamp = hours[predicted_lookahead][8]

    noaa_data_array.append([timeStamp, float(hours[predicted_lookahead][3]), float(hours[predicted_lookahead][4]), float(hours[predicted_lookahead][5]), float(hours[predicted_lookahead][6]), float(hours[predicted_lookahead][7])])
noaa_data_array = np.array(noaa_data_array)


#CLEAR SKY ------------------
# sets the location: latitude, longitude, and time zone
hnxloc = pv.location.Location(36.31357, -119.63164, 'US/Pacific')
#times = pd.DatetimeIndex(start='2019-02-27', end='2019-03-13', freq='60min')
times = pd.DatetimeIndex(noaa_data_array[:,0])
print(times)

# computes the clear sky model using a popular model
cs = hnxloc.get_clearsky(times, model='ineichen', linke_turbidity=3)


#PLOTTING --------------------

plt.plot(hourlySolradData[:,0], hourlySolradData[:,1], label = 'Direct')
#plt.plot(hourlySolradData[:,0], hourlySolradData[:,2], label = 'Diffuse')

#plt.plot(times, cs['dhi']*10, label = 'Clear sky')

plt.plot(times, cs['dhi']*(1 - noaa_data_array[:,2]/100)*10, label = 'Predicted clear')

#plt.plot(noaa_data_array[:,0],noaa_data_array[:,1]*10, label = 'temp')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,2], label = 'cloud-amount')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,3]*3, label = 'wind-speed')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,4]*3, label = 'humidity')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,5]*3, label = 'probability_of_precipitation')

plt.legend(loc = 'upper left')
plt.ylabel('Watts m^-2')
plt.xlabel('Time')
plt.show()
