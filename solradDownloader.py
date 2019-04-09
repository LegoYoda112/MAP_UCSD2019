import os
import ftplib

#FTP and file system code credit
#https://medium.com/@rrfd/ftp-access-with-python-1d096b061ef3

print('Connecting to server...')

locationName = 'hnx'

try:
    ftp = ftplib.FTP('aftp.cmdl.noaa.gov')
    ftp.login()
    print('Connected')
except ftplib.all_errors as e:
    errorcode_string = str(e).split(None, 1)[0]

#Setting the current working directory to 2019
ftp.cwd('/data/radiation/solrad/' + locationName + '/2019/')
#ftp.cwd('/data/radiation/solrad/realtime/' + locationName)

directoryName = 'solrad_data/' + locationName + '/'
if not os.path.exists(directoryName):
    os.makedirs(directoryName)

# Move into the folder
directoryPath = '%s/%s' % (os.getcwd(), directoryName)
os.chdir(directoryPath)

dateStart = 19090
dateEnd = 19094

currentDownloadDate = dateStart;

print( ftp.nlst())

while currentDownloadDate <= dateEnd:

    tempFileName = locationName + '%s.dat' % currentDownloadDate
    file = open(tempFileName, 'wb')

    print('Downloading %s' % tempFileName)

    try:
        ftp.retrbinary('RETR %s' % tempFileName, file.write)
        print('Successfully downloaded %s' % tempFileName)
    except ftplib.all_errors as e:
        print('Error downloading %s' % tempFileName)
        errorcode_string = str(e).split(None, 1)[0]

    currentDownloadDate += 1

ftp.close()
print('Closed')
