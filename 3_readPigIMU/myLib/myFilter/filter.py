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


class kalman_1D:

    def __init__(self, x0=0, p0=0, Q=1, R=1):
        self.__x = x0
        self.__p = p0
        self.__kal_Q = Q
        self.__kal_R = R
        logger.debug("init Q = %d", self.kal_Q)
        logger.debug("init R = %d", self.kal_R)

    @property
    def kal_Q(self):
        return self.__kal_Q

    @kal_Q.setter
    def kal_Q(self, Q):
        self.__kal_Q = Q
        # print("set kal_Q = ", Q)

    @property
    def kal_R(self):
        return self.__kal_R

    @kal_R.setter
    def kal_R(self, R):
        self.__kal_R = R
        # print("set kal_R = ", R)

    def update(self, z):
        k = self.__p / (self.__p + self.__kal_R)
        x = self.__x + k * (z - self.__x)
        p = (1 - k) * self.__p
        self.predict(x, p)
        return x

    def predict(self, x, p):
        self.__x = x
        self.__p = p + self.__kal_Q


class moving_average:
    def __init__(self, size):
        self.__sum = 0
        self.__data_arr = np.zeros(size)
        self.__ptr = 0

    def update(self, z):
        self.__data_arr[self.__ptr] = z
        self.__sum = np.sum(self.__data_arr)
        self.__ptr += 1
        if self.__ptr == len(self.__data_arr):
            self.__ptr = 0
        mv = self.__sum / len(self.__data_arr)
        # print(self.__ptr-1, end=", ")
        # print(self.__data_arr, end=", ")
        # print(self.__sum)
        return mv


if __name__ == "__main__":
    mv = moving_average(15)
    while 1:
        for i in range(10):
            avg = mv.update(1)
            print(avg)
        for i in range(10):
            avg = mv.update(2)
            print(avg)
