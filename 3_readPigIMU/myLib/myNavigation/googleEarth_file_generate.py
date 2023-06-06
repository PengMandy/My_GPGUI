""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys
import logging

import pandas as pd
import numpy as np
from numpy import sin, cos, arctan2
import time

from myLib.myNavigation import planar_Navigation
from myLib.myFilter import filter
import matplotlib.pyplot as plt

GOOGLE_EARTH_BLUE_START = ('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n' +
                           '<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n' +
                           '<Document>\n' +
                           '<Name>Session 1</Name>\n' +
                           '<Style id=\"redline\">\n' +
                           '<LineStyle>\n' +
                           '<color>ffff140a</color>\n' +
                           '<width>5</width>\n' +
                           '</LineStyle>\n' +
                           '</Style>\n' +
                           '<Placemark>\n' +
                           '<styleUrl>#redline</styleUrl>\n' +
                           '<LineString>\n' +
                           '<extrude>1</extrude>\n' +
                           '<tessellate>1</tessellate>\n' +
                           '<altitudeMode>clampedToGround</altitudeMode>\n' +
                           '<coordinates>')

GOOGLE_EARTH_BLACK_START = ('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n' +
                            '<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n' +
                            '<Document>\n' +
                            '<Name>Session 1</Name>\n' +
                            '<Style id=\"redline\">\n' +
                            '<LineStyle>\n' +
                            '<color>ff000000</color>\n' +
                            '<width>5</width>\n' +
                            '</LineStyle>\n' +
                            '</Style>\n' +
                            '<Placemark>\n' +
                            '<styleUrl>#redline</styleUrl>\n' +
                            '<LineString>\n' +
                            '<extrude>1</extrude>\n' +
                            '<tessellate>1</tessellate>\n' +
                            '<altitudeMode>clampedToGround</altitudeMode>\n' +
                            '<coordinates>')

GOOGLE_EARTH_END = ('</coordinates>\n' +
                    '</LineString>\n' +
                    '</Placemark>\n' +
                    '</Document>\n' +
                    '</kml>')


def main():
    filename = '0627_rt_2'
    man_mode_flag = True
    kalman_filter_flag = False
    arw = 0.0075
    navi = planar_Navigation.planarNav(kalman_filter=kalman_filter_flag)
    navi.kal.kal_R = 600
    if man_mode_flag:
        file_vbox = open('VBOX_' + filename + '.kml', 'w')
    else:
        file_vbox = open('VBOX_' + filename + '_all.kml', 'w')
    file_vbox.writelines(GOOGLE_EARTH_BLACK_START)
    Var = pd.read_csv(filename + '.txt', comment='#', skiprows=0, chunksize=None)
    print()
    print(filename + ' read done')
    print('**************************************')
    if man_mode_flag:
        print('track use manual mode, man_mode_flag = True')
    else:
        print('track use start up mode, man_mode_flag = False')

    if kalman_filter_flag:
        print('kalman filter enable')
        print('Kal_Q, kal_R: ', navi.kal.kal_Q, navi.kal.kal_R)
    else:
        print('kalman filter disable')
    print('**************************************')
    t_start = time.perf_counter()
    t = np.array(Var['time'])  # s
    update_period = (t[-1] - t[0]) / (len(t) - 1)
    print('update_rate: ', 1 / update_period)
    wz = np.array(Var['fog'])  # dps
    # wz = np.array(Var['wz'])  # dps
    speed = np.array(Var['speed']) / 3.6  # m/s
    hei = np.array(Var['Altitude'])  # m
    head = np.array(Var['Heading_KF'])
    vbox_ori_lon = Var['Longitude']
    vbox_ori_lat = Var['Latitude']
    vbox_lon_valid = Var['Longitude'] > 0
    vbox_lat_valid = Var['Latitude'] > 0
    vbox_lon = Var['Longitude'].loc[vbox_lon_valid]
    vbox_lat = Var['Latitude'].loc[vbox_lat_valid]
    size = len(t)
    print('size: ', size)
    if man_mode_flag:
        man_idx = abs(vbox_ori_lon - 121.714305).idxmin()
        # man_idx = abs(vbox_ori_lat - 24.847830).idxmin()
        man_idx2 = abs(vbox_ori_lon - 121.790530).idxmin()
    else:
        man_idx = 0
        man_idx2 = int((size - 1) / 1)
    print('man_idx, VBOX lon, VBOX lat @man_idx:　%d, %f, %f' % (man_idx, vbox_ori_lon[man_idx], vbox_ori_lat[man_idx]))
    print('man_idx2, VBOX lon, VBOX lat @man_idx2:　%d, %f, %f' % (
    man_idx2, vbox_ori_lon[man_idx2], vbox_ori_lat[man_idx2]))
    print()
    print('t[%d]: %f' % (man_idx, t[man_idx]))
    print('t[%d]: %f' % (man_idx2, t[man_idx2]))
    dt = round((t[man_idx2] - t[man_idx]) / 3600, 8)
    print('dt, sqrt(dt) [hr, sqrt(hr)]: ', round(dt, 5), round(dt ** 0.5, 5))
    print('ARW [deg/sqrt(hr)]: ', arw)
    print('accumulate drift caused by ARW(m): ', round((6400000 * arw * dt ** 0.5 * np.pi / 180), 5))
    print()
    lat0 = vbox_ori_lat[man_idx]
    lon0 = vbox_ori_lon[man_idx]
    # lat0 = 24.847830
    # lon0 = 121.791476
    hei0 = hei[man_idx]
    head0 = -head[man_idx] - 0.7

    # print('head0: ', head0)
    # head0 = -284
    track_lon = np.empty(0)
    track_lat = np.empty(0)

    navi.set_init(lat0=lat0, hei0=hei0, head0=head0, lon0=lon0)
    navi.t0 = t[man_idx] - update_period
    if kalman_filter_flag:
        file_imu = open('IMU_' + filename + "_" + str(head0) + '_man_KF_' + str(navi.kal.kal_R) + '.kml', 'w')
    else:
        file_imu = open('IMU_' + filename + "_" + str(head0) + '_man.kml', 'w')
    file_imu.writelines(GOOGLE_EARTH_BLUE_START)
    idx = 0

    for i in range(man_idx, man_idx2):
        idx += 1
        ecef_l, ecef_b = navi.track(t=t[i], wz=wz[i], speed=speed[i], hei=hei[i])
        # print('i: ', i)
        # print(ecef_l, ecef_b)
        track_lon = np.append(track_lon, ecef_l)
        track_lat = np.append(track_lat, ecef_b)
        if idx % 10 == 0:
            np.savetxt(file_imu, np.vstack([ecef_l, ecef_b, hei[i]]).T, fmt='%10.7f,%10.7f,%4.2f')
            if vbox_ori_lon[i] != 0 and vbox_ori_lat[i] != 0:
                np.savetxt(file_vbox, np.vstack([vbox_ori_lon[i], vbox_ori_lat[i], hei[i]]).T,
                           fmt='%10.7f,%10.7f,%4.2f')

    t_end = time.perf_counter()
    print('\ncode total running time cost: %f s\n' % (t_end - t_start))
    file_imu.writelines(GOOGLE_EARTH_END)
    file_imu.close()
    file_vbox.writelines(GOOGLE_EARTH_END)
    file_vbox.close()
    plt.subplot(121)
    if kalman_filter_flag:
        plt.title(filename + 'kalman (Q, R) = (' + str(navi.kal.kal_Q) + ', ' + str(navi.kal.kal_R) + ')')
    else:
        plt.title(filename)
    plt.plot(track_lon, track_lat, 'b-')
    plt.plot(vbox_lon, vbox_lat, 'r-')
    plt.xlabel('longitude', fontsize=20)
    plt.ylabel('latitude', fontsize=20)
    plt.legend(['IMU', 'VBOX'])
    plt.subplot(122)
    plt.plot(navi.yaw_gyro_return())
    plt.xlabel('pts', fontsize=20)
    plt.ylabel('dps', fontsize=20)
    plt.show()


if __name__ == '__main__':
    main()
