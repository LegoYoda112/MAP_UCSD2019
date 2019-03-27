import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import pvlib as pv
import math

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

            timeStamp = datetime(int(ordered_row[0]),int(ordered_row[2]),int(ordered_row[3]),int(ordered_row[4]),int(ordered_row[5]))
            ordered_row.append(timeStamp)

            ordered_file_contents.append(ordered_row)
            ordered_row = []

    ordered_file_contents = np.array(ordered_file_contents)

    #Closes file
    file.close()

    return ordered_file_contents

def readSolradRange(startDay, endDay):
    outputData = np.array(readSolradDataFile('solrad_data\\hnx' + str(startDay) + '.dat'))
    for day in range((startDay+1), (endDay+1)):
        filename = 'solrad_data\\hnx' + str(day) + '.dat'
        outputData = np.append(outputData, readSolradDataFile(filename), axis = 0)
    return outputData

#Read the solrad data
solradData = readSolradRange(19059,19077)


#Convert the solrad data into houly averages.
hourlySolradData = []

for i in range(0, int(len(solradData)/60)):
    hourOfSolradData = []
    timeStamp = solradData[(i*60)][22]
    for j in range(0, 59):
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

#NOAA READER ---------------------
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

#Number of ours to look ahead in our data.
predicted_lookahead = 1

noaa_data_array = []
for hours in ordered_hourly:
    timeStamp = hours[predicted_lookahead][8]

    noaa_data_array.append([timeStamp, float(hours[predicted_lookahead][3]), float(hours[predicted_lookahead][4]), float(hours[predicted_lookahead][5]), float(hours[predicted_lookahead][6]), float(hours[predicted_lookahead][7])])
noaa_data_array = np.array(noaa_data_array)


#LINING THE ARRAYS UP
#We need to make sure each array (solrad and noaa) is the same length and each index corrisponds to the same entry
startDate = datetime(2019,3,1,23,59)
endDate = datetime(2019,3,19)

#Trim the NOAA data
trimmed_noaa_data_array = []

for item in noaa_data_array:
    if((startDate < item[0]) & (endDate > item[0])):
        trimmed_noaa_data_array.append(item)
noaa_data_array = trimmed_noaa_data_array

#Trip the Solrad data
trimmed_solrad_data_array = []

for item in hourlySolradData:
    if((startDate < item[0]) & (endDate > item[0])):
        trimmed_solrad_data_array.append(item)

hourlySolradData = np.array(trimmed_solrad_data_array)

#Our downloaded noaa data has gaps, so we copy the previous values until we get another good data point
for index in range(0, len(hourlySolradData)):
    #print(hourlySolradData[index][0] == noaa_data_array[index][0])
    if(hourlySolradData[index][0] != noaa_data_array[index][0]):
        noaa_data_array.insert(index, noaa_data_array[index])


noaa_data_array = np.array(noaa_data_array)


#CALCULATING CLEAR SKY ------------------

# sets the location: latitude, longitude, and time zone
hnxloc = pv.location.Location(36.31357, -119.63164, 'US/Pacific')

#We create a times array that corrisponds to each entry in our trimmed arrays
times = pd.DatetimeIndex(hourlySolradData[:,0])

#Computes the clear sky (theoretical max) for each entry in the times array
cs = hnxloc.get_clearsky(times + timedelta(hours=0), model='ineichen', linke_turbidity=3)

#PLOTTING --------------------
plt.plot(times, hourlySolradData[:,1], label = 'Direct')
plt.plot(times, hourlySolradData[:,2], label = 'Diffuse')

plt.plot(times, cs['dhi'], label = 'Clear sky')

#plt.plot(times, (hourlySolradData[:,1]/(cs['dhi']*10))*100, label = 'Ratio')

#plt.plot(times, cs['dhi']*(1-noaa_data_array[:,2]/100)*10, label = 'Predicted')
plt.plot(times, (100-noaa_data_array[:,2]), label = 'Clouds')

#plt.plot(noaa_data_array[:,0],noaa_data_array[:,1], label = 'temp')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,2], label = 'cloud-amount')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,3], label = 'wind-speed')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,4], label = 'humidity')
#plt.plot(noaa_data_array[:,0],noaa_data_array[:,5], label = 'probability_of_precipitation')


plt.legend(loc = 'upper left')
plt.ylabel('Watts m^-2')
plt.xlabel('Time')
plt.show()


plt.scatter((100-noaa_data_array[:,5]), (hourlySolradData[:,1]/(cs['dhi']*10))*100)
plt.xlabel('Clouds - 1')
plt.ylabel('Solrad/clearsky')
plt.show()


#Machine learning
X = []
y = []
for index in range(1, len(noaa_data_array)-1):
    #print(cs['dhi'][index] != 0)
    X.append([noaa_data_array[index][2], noaa_data_array[index][3], noaa_data_array[index][4], noaa_data_array[index][5], cs['dhi'][index]])
    y.append(hourlySolradData[index][1])

    #If we use the output of the net as the ratio
    # if(cs['dhi'][index] != 0):
    #     X.append([noaa_data_array[index][2], noaa_data_array[index][4], noaa_data_array[index][5]])
    #     y.append((hourlySolradData[index][1]/(cs['dhi'][index])))

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

#train_scaled = scaler.fit_transform(X_train)
#test_scaled = scaler.transform(X_test)

print("Test")

from sklearn.neural_network import MLPRegressor

model = MLPRegressor(max_iter = 1000, verbose = True, hidden_layer_sizes=(100,10), solver = 'adam')

model.fit(X_train, y_train)

#plt.scatter(y_train, model.predict(X_train), label = 'Direct')
#plt.show()



plt.plot(times, hourlySolradData[:,1], label = 'Actual')

predictInputs = []
for index in range(0, len(noaa_data_array)):
    predictInputs.append([noaa_data_array[index][2], noaa_data_array[index][3], noaa_data_array[index][4], noaa_data_array[index][5], cs['dhi'][index]])

plt.plot(times, cs['dhi']*(1-noaa_data_array[:,2]/100)*10, label = 'Predicted using just cloud %')

plt.plot(times, (model.predict(predictInputs)), label = 'Predicted using MLPRegressor')

#plt.plot(times, cs['dhi']*(model.predict(predictInputs)), label = 'Predicted')
plt.legend(loc = 'upper left')
plt.show()

params = model.get_params()

from joblib import dump

dump(model, 'MLPRegressor_model.joblib')
print('Model has been dumped')
