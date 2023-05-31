import sys
import logging

import pandas as pd
import numpy as np
from numpy import sin, cos, arctan2
import time

from myLib.myNavigation import planar_Navigation
from myLib.myFilter import filter
import matplotlib.pyplot as plt


def main():
    filename = '0628_rt_3'
    man_mode_flag = True
    kalman_filter_flag = False
    arw = 0.0075
    navi = planar_Navigation.planarNav(kalman_filter=kalman_filter_flag)
    navi.kal.kal_R = 6
    # file_vbox = open('VBOX_' + filename + '.kml', 'w')
    # file_vbox.writelines(GOOGLE_EARTH_BLACK_START)
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

    var1 = vbox_ori_lon[abs(vbox_ori_lon - 121.791476) < 1e-4]
    idx1 = var1.index
    var2 = vbox_ori_lat[abs(vbox_ori_lat - 24.847830) < 1e-4]

    print(var1)
    print(var2)


if __name__ == '__main__':
    main()
