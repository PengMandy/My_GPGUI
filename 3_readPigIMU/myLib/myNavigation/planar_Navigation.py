# -*- coding:UTF-8 -*-
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

import numpy as np
from numpy import sin, cos, arctan2
import time
from myLib.myFilter import filter

radius_a = 6378137
radius_b = 6356752.3142
eccen = 0.08181929
eccenp = ((radius_a ** 2 - radius_b ** 2) / (radius_b ** 2)) ** 0.5


class planarNav:

    def __init__(self, kalman_filter=False):
        self.is_rate_pass = False
        self.__head0 = None
        self.t0 = 0
        self.cnt = 0
        self.kal = filter.kalman_1D()
        self.__kal_en = kalman_filter
        self.wz_array = np.empty(0)

    def set_init(self, lat0, lon0, hei0, head0):
        self.lat0 = lat0
        self.lon0 = lon0
        self.hei0 = hei0
        self.head0 = head0
        self.theta_w = 0
        self.x_w = 0
        self.y_w = 0

        RN = radius_a / (1 - (eccen ** 2) * ((sin(self.lat0 * np.pi / 180)) ** 2)) ** 0.5
        ecef_x0 = (RN + hei0) * cos(lat0 * np.pi / 180) * cos(lon0 * np.pi / 180)
        ecef_y0 = (RN + hei0) * cos(lat0 * np.pi / 180) * sin(lon0 * np.pi / 180)
        ecef_z0 = (RN * (1 - eccen ** 2) + hei0) * sin(lat0 * np.pi / 180)
        self.Vec_ecef_xyz0 = np.array([[ecef_x0], [ecef_y0], [ecef_z0]])
        self.Rn2e = np.array([
            [-sin(lon0 * np.pi / 180), -sin(lat0 * np.pi / 180) * cos(lon0 * np.pi / 180),
             cos(lat0 * np.pi / 180) * cos(lon0 * np.pi / 180)],
            [cos(lon0 * np.pi / 180), -sin(lat0 * np.pi / 180) * sin(lon0 * np.pi / 180),
             cos(lat0 * np.pi / 180) * sin(lon0 * np.pi / 180)],
            [0, cos(lat0 * np.pi / 180), sin(lat0 * np.pi / 180)]
        ])
        print('set Navi. init.lat0: ', lat0)
        print('set Navi. init.lon0: ', lon0)
        print('set Navi. init.hei0: ', hei0)
        print('set Navi. init.head0: ', head0)

    def track(self, t, wz, speed, hei):
        dt = round((t - self.t0), 3)
        self.t0 = t
        # print('dt:', dt)
        # print('wz:', wz)
        # print('speed:', speed)
        if self.__kal_en:
            wz = self.kal.update(wz)
        self.wz_array = np.append(self.wz_array, wz)
        self.theta_w = self.theta_w - wz * dt  # accumulate theta in w-frame
        self.x_w = self.x_w + speed * np.sin(self.theta_w * np.pi / 180) * dt  # x in w-frame
        self.y_w = self.y_w + speed * np.cos(self.theta_w * np.pi / 180) * dt  # y in w-frame
        x_l = self.x_w * np.cos(self.head0 * np.pi / 180) - self.y_w * np.sin(self.head0 * np.pi / 180)  # x in l-frame
        y_l = self.x_w * np.sin(self.head0 * np.pi / 180) + self.y_w * np.cos(self.head0 * np.pi / 180)  # y in l-frame
        enu_xyz = np.array([[x_l], [y_l], [hei - self.hei0]])  # l-frame ENU coordinate
        Vec_ecef_xyz = self.Vec_ecef_xyz0 + self.Rn2e.dot(enu_xyz)  # ECEF coordinate
        ecef_x = Vec_ecef_xyz[0]
        ecef_y = Vec_ecef_xyz[1]
        ecef_z = Vec_ecef_xyz[2]
        THE = arctan2((ecef_z * radius_a), (((ecef_x ** 2 + ecef_y ** 2) ** 0.5) * radius_b)) * 180 / np.pi
        ecef_b = arctan2((ecef_z + (eccenp ** 2) * radius_b * ((sin(THE * np.pi / 180)) ** 3)),  # latitude
                         ((ecef_x ** 2 + ecef_y ** 2) ** 0.5 - (eccen ** 2) * radius_a * (
                                 (cos(THE * np.pi / 180)) ** 3))) * 180 / np.pi
        ecef_l = arctan2(ecef_y, ecef_x) * 180 / np.pi  # longitude

        return ecef_l, ecef_b

        # if self.is_rate_pass:
        #     return ecef_l, ecef_b
        #     self.is_rate_pass = False

    def yaw_gyro_return(self):
        return self.wz_array

    def output_rate(self, rate):
        period = 1 / rate
        if (time.perf_counter() - self.cnt) > period:
            self.is_rate_pass = True

    @property
    def is_rate_pass(self):
        return self.__is_rate_pass

    @is_rate_pass.setter
    def is_rate_pass(self, val):
        self.__is_rate_pass = val

    @property
    def head0(self):
        return self.__head0

    @head0.setter
    def head0(self, head):
        self.__head0 = head

    @property
    def t0(self):
        return self.__t0

    @t0.setter
    def t0(self, t0):
        self.__t0 = t0
