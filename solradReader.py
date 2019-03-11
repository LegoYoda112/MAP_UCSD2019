##   ---- KEY ---- (from README_SOLRAD.txt)

## - In header -
#station_name	character	station name, e. g., Goodwin Creek
#latitude	real	latitude in decimal degrees (e. g., 40.80)
#longitude	real	longitude in decimal degrees (e. g., 105.12)
#elevation	integer	elevation above sea level in meters
#h_to_lst	integer hours displaced from local standard time

#year		integer	year, i.e., 2002
#jday		integer	Julian day (1 through 365 [or 366])
#month		integer	number of the month (1-12)
#day		integer	day of the month(1-31)
#hour		integer	hour of the day (0-23)
#min		integer	minute of the hour (0-59)
#dt		real	decimal time (hour.decimalminutes),e. g., 23.5 = 2330
#zen		real	solar zenith angle (degrees)
#dw_psp		real	downwelling global solar (Watts m^-2)
#direct		real	direct solar (Watts m^-2)
#diffuse		real	downwelling diffuse solar (Watts m^-2)
#uvb		real	global UVB (milliWatts m^-2)
#uvb_temp    	real	UVB temperature (C) -- 25 deg. C is normal
#qc_dwpsp	integer quality control parameter for downwelling global solar (0=good)
#qc_direct	integer quality control parameter for direct solar (0=good)
#qc_diffuse	integer quality control parameter for diffuse solar (0=good)
#qc_uvb		integer quality control parameter for UVB irradiance (0=good)
#qc_uvb_temp	integer quality control parameter for the UVB instrument temperature (0=good)
#std_dw_psp	real	standard deviation of the 1-sec. samples for global solar (dw_psp)
#std_direct	real	standard deviation of the 1-sec. samples for direct solar
#std_diffuse	real	standard deviation of the 1-sec. samples for diffuse solar
#std_uvb		real	standard deviation of the 1-sec. samples for uvb

 #year,jday,month,day,hour(i),min(i),dt(i),
 #1	zen(i),dw_psp(i),qc_dwpsp(i),direct(i),qc_direct(i),
 #2	diffuse(i),qc_diffuse(i),uvb(i),qc_uvb(i),uvb_temp(i),
 #3  qc_uvb_temp(i),std_dw_psp(j),std_direct(j),std_diffuse(j),
 #4  std_uvb(j)

#example
# year,jday,month,day,hour,min,dt,     zen, dw_psp,qc_dwpsp, direct,qc_direct, diffuse,qc_diffuse, uvb,qc_uvb, uvb_temp,qc_uvb_temp, std_dw_psp,std_direct,std_diffuse,std_uvb
#2019   1    1    1   0    0   0.000   81.55  79.6   0         229.6   0          55.8      0       3.4   0      42.7       0           0.475      0.581      0.358      0.042

import pandas as pd
import re

#Opens the file
file = open('solrad_data\\hnx19002.dat', 'r')

#Reads the file
raw_file_contents = file.read()

file_contents = raw_file_contents.split(" ")

for item in file_contents:
    if item == '':
        file_contents.remove(item)

print(file_contents)
