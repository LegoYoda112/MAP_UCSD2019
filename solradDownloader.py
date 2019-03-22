import os
import ftplib

#FTP and file system code credit
#https://medium.com/@rrfd/ftp-access-with-python-1d096b061ef3

print 'Connecting to server...'

try:
    ftp = ftplib.FTP('aftp.cmdl.noaa.gov')
    ftp.login()
    print 'Connected'
except ftplib.all_errors, e:
    errorcode_string = str(e).split(None, 1)[0]

#Setting the current working directory to 2019
ftp.cwd('/data/radiation/solrad/hnx/2019/')

directoryName = 'solrad_data'
if not os.path.exists(directoryName):
    os.makedirs(directoryName)

# Move into the folder
directoryPath = '%s/%s' % (os.getcwd(), directoryName)
os.chdir(directoryPath)

dateStart = 19076;
dateEnd = 19078;

currentDownloadDate = dateStart;

print ftp.nlst()

while currentDownloadDate <= dateEnd:

    tempFileName = 'hnx%s.dat' % currentDownloadDate
    file = open(tempFileName, 'wb')

    print 'Downloading %s' % tempFileName

    try:
        ftp.retrbinary('RETR %s' % tempFileName, file.write)
        print 'Successfully downloaded %s' % tempFileName
    except ftplib.all_errors, e:
        print 'Error downloading %s' % tempFileName
        errorcode_string = str(e).split(None, 1)[0]

    currentDownloadDate += 1

ftp.close()
print 'Closed'
