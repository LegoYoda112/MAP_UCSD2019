import pandas as pd
import numpy
import matplotlib.pyplot as plt
import pvlib as pv
import datetime as dt

# sets the location: latitude, longitude, and time zone
hnxloc = pv.location.Location(36.31357, -119.63164, 'US/Pacific')
times = pd.DatetimeIndex(start='2016-07-01', end='2016-07-04', freq='1min')

# computes the clear sky model using a popular model
cs = hnxloc.get_clearsky(times, model='ineichen', linke_turbidity=3)

print(cs)
plt.plot(times, cs['dni'])
plt.show()
