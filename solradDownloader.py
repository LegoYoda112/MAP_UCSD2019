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

ftp.cwd('/data/radiation/solrad/hnx/2019/')

directoryName = 'solrad_data'
if not os.path.exists(directoryName):
    os.makedirs(directoryName)

# Move into the folder
directoryPath = '%s/%s' % (os.getcwd(), directoryName)
os.chdir(directoryPath)

ftp.close()
print 'Closed'
