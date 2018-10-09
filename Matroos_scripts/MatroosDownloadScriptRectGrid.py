import requests
from datetime import datetime, timedelta
import numpy
import os

# User Inputs
start_time = datetime(2018, 9, 28, 19, 00)
duration = 3 # hours
#SpillPosition = (5.865809, 53.414650, 0)     # somewhere east near mudflats
SpillPosition = (4.7483892, 52.976501, 0)  # den helder-Tx
#SpillPosition = (4.176284, 52.302249, 0) # Noordwijk
#SpillPosition = (5.006956, 54.472957,0) # Way up north
#SpillPosition = (6.280000, 53.410000 ,0) # Lauwersoog
WindS = (0, 270)  # Wind speed 'm/s' & direction (degrees) (180 = from South)
# LocalDownload = No, defaults to downloading the WaddenZee region
# LocalDownload = Yes, downloads local area, large enough to fit probable displacement of the slick within duration
LocalDownload = 'Yes'
# CleanDiskPolicy = 'Yes', the downloaded file will be removed from the computer after finishing the script
CleanDiskPolicy = 'No'

'''
NetCDF GNOME download link
http://noos.matroos.rws.nl:80//matroos/scripts/matroos.pl?source=dcsmv6_zunov4_zuno_kf_hirlam&anal=000000000000&z=0
&xmin=5&xmax=6&ymin=52.9&ymax=53&coords=WGS84&xmin_abs=-4.3000001907349&xmax_abs=9.6000003814697&ymin_abs=49.200000762939
&ymax_abs=57.200000762939&color=VELU,VELV&interpolate=size&now=201809200000&to=201809220600&from=201809220500
&outputformat=nc_gnome&stridex=&stridey=&stridetime=1&xn=1449&yn=638&celly=17&cellx=46&fieldoutput=,&format=nc
'''

# Initialize fixed parameters
payload = {'source': 'dcsmv6_zunov4_zuno_kf_hirlam',  # Dataset with
           'anal': '000000000000',  # most recent analyse time
           'z': '0',  #
           'coords': 'WGS84',  # keep the coordinate system
           'xmin_abs': '-4.3000001907349', 'xmax_abs': '9.6000003814697',  # absolute dataset bounds zunov4
           'ymin_abs': '49.200000762939', 'ymax_abs': '57.200000762939',  # absolute dataset bounds zunov4
           'color': 'VELU,VELV',  # get water speed (U & V) and depth (water level)
           'interpolate': 'size',
           'outputformat': 'nc_gnome',
           'stridex': '1', 'stridey': '1',  # don't interpolate geographically, keep the native grid
           # interpolate the output time. Timestepvalue: 1=0.2 hours,6=1.0 h
           'stridetime': '6',
           'xn': '1449', 'yn': '638', 'celly': '161', 'cellx': '128',
           'fieldoutput': ',',
           'format': 'nc',
           # by default use WaddenzeeWest Area, can be updated later
           'xmin': '4.556330', 'xmax': '7.364830',
           'ymin': '52.845370', 'ymax': '53.755460'
           }

# calculate variable parameters
i = datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
stop_time = start_time + timedelta(hours=duration)
payload['now'] = i.strftime('%Y%m%d%H%M')
payload['to'] = stop_time.strftime('%Y%m%d%H%M')
payload['from'] = start_time.strftime('%Y%m%d%H%M')
if LocalDownload == 'Yes':
    maxdist = (1.5 * numpy.minimum(duration, 10) * 3600) + WindS[0] * duration * 3600
    dxmax = numpy.maximum(0.5, maxdist / (111.320 * numpy.cos(numpy.deg2rad(SpillPosition[1])) * 1000))
    xmin = SpillPosition[0] - dxmax
    xmax = SpillPosition[0] + dxmax
    dymax = numpy.maximum(0.2, maxdist / 110540)
    ymin = SpillPosition[1] - dymax
    ymax = SpillPosition[1] + dymax
    payload['xmin'] = str(round(xmin, 6))
    payload['xmax'] = str(round(xmax, 6))
    payload['ymin'] = str(round(ymin, 6))
    payload['ymax'] = str(round(ymax, 6))
    payload['xn'] = str(int(round((((xmax - xmin) * (111.320 * numpy.cos(numpy.deg2rad(SpillPosition[1])) * 1000))/150))))
    payload['yn'] = str(int(round((((ymax - ymin) * 110540)/150))))

# check if times are within range of available data:
mintime = i - timedelta(days=7)
maxtime = i + timedelta(days=2)
if start_time < mintime:
    print('Choose a start time after: %s' % mintime.strftime('%d-%m-%Y %H:%M'))
if stop_time > maxtime:
    print('End of simulation is beyond available data: %s' % maxtime.strftime('%d-%m-%Y %H:%M'))

# download dataset
print('Downloading dataset')
url = 'http://noos.matroos.rws.nl:80//matroos/scripts/matroos.pl'
r = requests.get(url, params=payload, allow_redirects=True)
open('MatroosRect.nc', 'wb').write(r.content)
print(r.url)
del r

# Check if it the download works by plotting the full grid, and the vectors of a smaller portion
print('Creating images')
import netCDF4
import matplotlib.pyplot as plt
import numpy

DS = netCDF4.Dataset("MatroosRect.nc")

print(DS)
x = DS.variables['x'][:] # .variables['lon'][:]
y = DS.variables['y'][:] # .variables['lat'][:]
x, y = numpy.meshgrid(x, y)

t = 0
X = DS.variables['x'][:]
Y = DS.variables['y'][:]
U = DS.variables['VELU'][t, :, :]
V = DS.variables['VELV'][t, :, :]
X, Y = numpy.meshgrid(X, Y)

fig, (fig0, fig1) = plt.subplots(ncols=2, figsize=(20, 10))
fig0.plot(x, y)
fig0.set_title('full grid')

sset = 1
fig1.quiver(X[::sset, ::sset], Y[::sset, ::sset], U[::sset, ::sset], V[::sset, ::sset],
            edgecolor='k', scale=40, headwidth=3, width=0.001)
fig1.set_xlim([numpy.min(X), numpy.max(X)])
fig1.set_ylim([numpy.min(Y), numpy.max(Y)])
fig1.set_title('vectors of portion of grid')
fig1.text(numpy.max(X), numpy.min(Y), '''vector per %d gridcells
''' % sset,
          horizontalalignment='right', verticalalignment='bottom')
fig1.text(numpy.min(X), numpy.max(Y), '''
     %s''' % start_time.strftime('%d-%m-%Y %H:%M'),
          horizontalalignment='left', verticalalignment='top')
fig.tight_layout()
plt.show()

if CleanDiskPolicy == 'Yes':
    print('Removing downloaded file')
    DS.close()
    os.remove("MatroosRect.nc")