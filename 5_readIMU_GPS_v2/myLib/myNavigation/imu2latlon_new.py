#%%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from osgeo import osr
from spatialmath import *


# ============================================= #
# ====== enter initialization parametets ====== #
# ============================================= #

# operational parameters == HERE
calID = 1
figID = 1
gpxID = 1

# set the initial conditions == HERE
lat0  =  25.04157972962935												# initial wgs84 latitude in degree
lon0  =  121.5363068740776												# initial wgs84 lontitude in degree
phi0  = -9.398348																	# initial azimuth of the y axis in degree
ele0  =  30																				# initial elevation

# enter the file name of imu data == HERE
fimeName = '220929_static.txt'

g0 = 9.80665																			# local g-value
dax, day, daz = 0, 0, 1														# accerating bias calibration
if calID == 1:
	dax = 0.014942367197875162
	day = 0.004572687583001328
	daz = 0.984853980743692


# ============================================= #
# == transform spatial reference coordinates == #
# ============================================= #

proj_crs = osr.SpatialReference()
proj_crs.ImportFromEPSG(3826)											# crs: twd97 / tm2 zone 121
proj_gcs = osr.SpatialReference()
proj_gcs.ImportFromEPSG(4326)											# gcs: wgs84

def crs2gcs(pnt):
    trans = osr.CoordinateTransformation(proj_crs, proj_gcs)
    newx, newy, _ = trans.TransformPoint(float(pnt[0]), float(pnt[1]))
    return [newx, newy]
	
def gcs2crs(pnt):
    trans = osr.CoordinateTransformation(proj_gcs, proj_crs)
    newx, newy, _ = trans.TransformPoint(float(pnt[0]), float(pnt[1]))
    return [newx, newy]
	
def crs2crs(pnt, proj1, proj2):
		proj_crs1=osr.SpatialReference()
		proj_crs1.ImportFromEPSG(proj1)
		proj_crs2=osr.SpatialReference()
		proj_crs2.ImportFromEPSG(proj2)
		trans = osr.CoordinateTransformation(proj_crs1, proj_crs2)
		newx, newy, _ = trans.TransformPoint(float(pnt[0]), float(pnt[1]))
		return [newx, newy]


# ============================================= #
# ============== import imu data ============== #
# ============================================= #

# load the starting datetime of imu data
with open(fimeName) as f:
  imuTime0 = f.readline()[1:-1]
imuTime0 = datetime.strptime(imuTime0, '%Y/%m/%d %H:%M:%S')

# load imu data with pandas
colList  = ['time', 'fog', 'wx', 'wy', 'ax', 'ay', 'az']
skipRows = list(range(2, 19))
skipRows.insert(0, 0)
imuData = pd.read_csv(fimeName, sep = ',', skiprows = skipRows, skipfooter = 1, usecols = colList, engine = 'python')


# ============================================= #
# ======= find the track using imu data ======= #
# ============================================= #

X = np.zeros((len(imuData), 3))
R = SE3.Rz(-phi0, 'deg')

for row in np.arange(len(imuData) -1):

	t0, wz0, wx0, wy0, ax0, ay0, az0 = imuData.loc[row]
	t1 = imuData["time"].loc[row + 1]

	[ax0, ay0, az0] = [ax0 - dax, ay0 - day, az0 - daz]

	[phiX, phiY, phiZ] = [(t1 - t0) * w      for w in [wx0, wy0, wz0]]
	[velx, vely, velz] = [(t1 - t0) * a * g0 for a in [ax0, ay0, az0]]

	P = R * SE3(velx, vely, velz)

	X[row + 1, :] = np.transpose(P * X[0, :]) + X[row, :]
	#R = SE3.Rz(phiZ, 'deg') * R
	R = SE3.Ry(phiY, 'deg') * SE3.Rx(phiX, 'deg') * SE3.Rz(phiZ, 'deg') * R

[crsx0, crsy0] = gcs2crs([lat0, lon0])

X = X + [crsx0, crsy0, ele0]

for K in np.arange(len(X)):
	X[K, [0, 1]] = crs2gcs(X[K, [0, 1]])


# ============================================= #
# ============ visualize the track ============ #
# ============================================= #

if figID == 1:

	#plt.plot(imuData['time'], X[:, 0])
	#plt.show()
	#plt.plot(imuData['time'], X[:, 1])
	#plt.show()
	plt.plot(imuData['time'], X[:, 2])
	plt.show()
	plt.plot(X[:, 1], X[:, 0])
	plt.show()


# ============================================= #
# ======== export imu data as gpx file ======== #
# ============================================= #

if gpxID == 1:

	gpxName = fimeName[:-4] + '_new.gpx'
	gpxMetaTime = imuTime0.isoformat(timespec='milliseconds')
	with open(gpxName, 'w', encoding='utf8') as gpx:

		# write gpx header
		gpx.write(r'<?xml version="1.0" encoding="UTF-8" ?>' + '\n')
		gpx.write(r'<gpx version="1.1" creator="URT Co. Ltd." xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">' + '\n\n')

		# write metadata
		gpx.write( '  <metadata>\n')
		gpx.write(f'    <name>' + gpxName + '</name>\n')
		gpx.write(f'    <time>' + gpxMetaTime + 'Z</time>\n')
		gpx.write( '  </metadata>\n\n')

		# construct <trk> and <trkseg>
		gpx.write('  <trk>\n    <trkseg>\n')

		# compute the lon lat by imu data
		for K in np.arange(len(X)):

			lat, lon = X[K, [0, 1]]
			imuTime  = imuTime0 + timedelta(seconds = imuData['time'][K]) - timedelta(hours = 8)
			
			# write <trkpt> with timestamps
			gpx.write(f'      <trkpt lat="' + str(lat) + '" lon="' + str(lon) + '">\n')
			gpx.write(f'        <time>' + imuTime.isoformat(timespec = 'milliseconds') + 'Z</time>\n')
			gpx.write(f'        <ele>' + str(X[K, 2]) + '</ele>\n')
			gpx.write( '      </trkpt>\n')

		# end <trk>, <trkseg>, and <gpx>
		gpx.write('    </trkseg>\n  </trk>\n\n')
		gpx.write('</gpx>\n')

		print('The gpx file has been created!')


# ============================================= #
# ==================== END ==================== #
# ============================================= #

# %%
