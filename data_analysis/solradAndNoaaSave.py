import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from datetime import timedelta
import pvlib as pv
import math
import os

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

locationName = 'hnx'
#TODO: Figure out why slc isn't working

master_directory = os.path.dirname(os.getcwd())
data_directory = master_directory + '\\data\\'
noaa_directory = data_directory + '\\noaa\\'
solrad_directory = data_directory + 'solrad_data\\' + locationName + '\\'

#SOLRAD READER -----------------
def readSolradDataFile (filename):
    print('Reading ' + filename)

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

    for i in range(0, len(cleaned_file_contents)-7):
        row = i % rowLength
        item = float(cleaned_file_contents[i+offset])

        if(item<-100):
            item = -100

        ordered_row.append(item)

        #print(row, column, item)

        if(row == rowLength-1):
            column +=1

            timeStamp = datetime(int(ordered_row[0]),int(ordered_row[2]),int(ordered_row[3]),int(ordered_row[4]),0)
            ordered_row.append(timeStamp)

            ordered_file_contents.append(ordered_row)
            ordered_row = []

    ordered_file_contents = np.array(ordered_file_contents)

    #Closes file
    file.close()

    return ordered_file_contents

def readSolradRange(startDay, endDay):
    file_path = solrad_directory + locationName + str(startDay) + '.dat'
    outputData = np.array(readSolradDataFile(file_path))
    for day in range((startDay+1), (endDay+1)):
        file_path = solrad_directory + locationName + str(day) + '.dat'
        outputData = np.append(outputData, readSolradDataFile(file_path), axis = 0)
    return outputData

#Read the solrad data
solradData = readSolradRange(19060,19122)

#Convert the solrad data into houly averages.
hourlySolradData = []

for i in range(1, int(len(solradData)/60)-1):
    hourOfSolradData = []
    timeStamp = solradData[(i*60)][22]
    for j in range(0, 59):
        direct = solradData[(i*60)+j-30][10]
        diffuse = solradData[(i*60)+j-30][12]
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

#NOAA READER ---------------------
csv_array = pd.read_csv(noaa_directory + 'noaa-' + locationName + '.csv').as_matrix()

ordered_hourly = []
hourly_forecast = []
hour_forecast = []

hours_per_forecast = 168

#2019-02-26T15:00:00-08:00

for i in range(0,len(csv_array)-1):
    if((i+1) % hours_per_forecast == 0):
        ordered_hourly.append(np.array(hourly_forecast))
        hourly_forecast = []

    time = csv_array[i][2]
    timezoneOffset = int(time[-5:-3])
    time = datetime.strptime(time[:-9], '%Y-%m-%dT%H:%M') + timedelta(hours = timezoneOffset)

    hour_forecast = csv_array[i]
    hour_forecast = np.append(hour_forecast, time)

    hourly_forecast.append(hour_forecast)


ordered_hourly = np.array(ordered_hourly)


noaa_data_array = []
predicted_lookahead = 48

for hours in ordered_hourly:
    hours = np.array(hours)
    timeStamp = hours[predicted_lookahead][8]

    noaa_data_array.append([timeStamp, float(hours[predicted_lookahead][3]), float(hours[predicted_lookahead][4]), float(hours[predicted_lookahead][5]), float(hours[predicted_lookahead][6]), float(hours[predicted_lookahead][7])])

noaa_data_array = np.array(noaa_data_array)


#LINING THE ARRAYS UP
#We need to make sure each array (solrad and noaa) is the same length and each index corrisponds to the same entry
startDate = datetime(2019,3,1)
endDate = datetime(2019,5,1)

#Trim the NOAA data
trimmed_noaa_data_array = []

for item in noaa_data_array:
    if((startDate < item[0]) & (endDate > item[0])):
        trimmed_noaa_data_array.append(item)
noaa_data_array = trimmed_noaa_data_array

print(noaa_data_array[len(noaa_data_array)-1])

#Trip the Solrad data
trimmed_solrad_data_array = []

for item in hourlySolradData:
    if((startDate < item[0]) & (endDate > item[0])):
        trimmed_solrad_data_array.append(item)
hourlySolradData = np.array(trimmed_solrad_data_array)

print(hourlySolradData[len(hourlySolradData)-1])

#Our downloaded noaa data has gaps, so we copy the previous values until we get another good data point
for index in range(0, len(hourlySolradData)-1):
    #print(hourlySolradData[index][0] == noaa_data_array[index][0])
    if(hourlySolradData[index][0] != noaa_data_array[index][0]):
        noaa_data_array.insert(index, noaa_data_array[index])

noaa_data_array = np.array(noaa_data_array)

#CALCULATING CLEAR SKY ------------------

# sets the location: latitude, longitude, and time zone
hnxloc = pv.location.Location(36.19, -119.38)

#We create a times array that corrisponds to each entry in our trimmed arrays
times = pd.DatetimeIndex(hourlySolradData[:,0])

#Computes the clear sky (theoretical max) for each entry in the times array
cs = hnxloc.get_clearsky(times, model='ineichen', linke_turbidity=3)

print('Solrad length')
print(len(hourlySolradData))
print('NOAA length')
print(len(noaa_data_array))

#PLOTTING --------------------
#plt.plot(hourlySolradData[:,1], label = 'Direct')
#plt.plot(hourlySolradData[:,1], label = 'Direct')
#plt.plot(hourlySolradData[:,3], label = 'Diffuse')

#plt.plot(cs['dni'], label = 'Clear sky')

#plt.plot(times, (hourlySolradData[:,1]/(cs['dhi']*10))*100, label = 'Ratio')

#plt.plot(times, cs['dhi']*(1-noaa_data_array[:,2]/100), label = 'Predicted')
#plt.plot((100-noaa_data_array[:,2]), label = 'Clouds')
#

#f, axarr = plt.subplots(2, sharex=True)

fig = plt.figure()

ax1 = plt.subplot(2, 1, 1)
plt.plot(times,noaa_data_array[:,1], label = 'temp')
plt.plot(times, noaa_data_array[:,2], label = 'cloud-amount')
plt.plot(times, noaa_data_array[:,3], label = 'wind-speed')
plt.legend(loc = 'upper left')
ax2 = plt.subplot(2, 1, 2, sharex = ax1)

plt.plot(times, hourlySolradData[:,1], label = 'Direct')
plt.plot(times, hourlySolradData[:,3], label = 'Diffuse')
plt.legend(loc = 'upper left')
plt.setp(ax1.get_xticklabels(), visible=False)

fig.tight_layout()

plt.show()

outputData = []

for index in range(1, len(noaa_data_array)-1):
    outputData.append([hourlySolradData[index][0], hourlySolradData[index][1], hourlySolradData[index][2], hourlySolradData[index][3], hourlySolradData[index][4], noaa_data_array[index][1], noaa_data_array[index][2], noaa_data_array[index][3], noaa_data_array[index][4], noaa_data_array[index][5], cs['dni'][index]])


file_name = 'savedData.csv'
predictedDF = pd.DataFrame(outputData, columns = ["timestamp","direct", "directSD", "diffuse", "diffuseSD", 'temp', 'cloud_amount', 'wind_speed', 'humidity','probability_of_precipitation', 'clear_sky'])
predictedDF.to_csv(file_name, encoding='utf-8', header = True)
#predictedDF.to_csv(file_name, encoding='utf-8', mode = 'a', header = False)
