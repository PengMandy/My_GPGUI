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
from datetime import datetime
sys.path.append("../")
from myLib.mySerial.Connector import Connector
from myLib.mySerial import getData
from myLib.crcCalculator import crcLib
from myLib.myFilter import filter
import time
from PyQt5.QtCore import QThread, pyqtSignal
from myLib import common as cmn
import numpy as np
import logging

# from pig_parameters import *

PRINT_DEBUG = 0

IMU_DATA_STRUCTURE = {
    "NANO33_WX": np.zeros(1),
    "NANO33_WY": np.zeros(1),
    "NANO33_WZ": np.zeros(1),
    "NANO33_AX": np.zeros(1),
    "NANO33_AY": np.zeros(1),
    "NANO33_AZ": np.zeros(1),
    "ADXL_AX": np.zeros(1),
    "ADXL_AY": np.zeros(1),
    "ADXL_AZ": np.zeros(1),
    "TIME": np.zeros(1),
    'YEAR': np.zeros(1),
    'MON': np.zeros(1),
    'DAY': np.zeros(1),
    'HOUR': np.zeros(1),
    'MIN': np.zeros(1),
    'SEC': np.zeros(1),
    'mSEC': np.zeros(1),
    'DATA_CNT': np.zeros(1),
    'GPS_ALIVE': np.zeros(1)
}

GPS_DATA_STRUCTURE = {
    'GPS_DATE': np.zeros(1),
    'GPS_TIME': np.zeros(1),
    'CNT': np.zeros(1)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = 4
POS_NANO33_WX = 13
POS_DATE = 25
# POS_PIG = 25
# POS_CRC = 35
old = time.perf_counter_ns()


class memsImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object)
        imuThreadStop_qt = pyqtSignal()
        buffer_qt = pyqtSignal(int)

    def __init__(self, portName: str = "None", boolCaliw=False, boolCalia=False, baudRate: int = 230400,
                 debug_en: bool = 0):
        super(memsImuReader, self).__init__()
        self.__carry_ms = 0
        self.date_type = 'PC'
        self.__carry_mm = 0
        self.__carry_ss = 0
        self.__dataRate = 250
        self.nano33_wz_kal = filter.kalman_1D()
        # self.pig_wz_kal = filter.kalman_1D()
        self.__isCali_a = boolCalia
        self.__isCali_w = boolCaliw
        self.sf_a = 1
        self.sf_b = 0
        self.isKal = False
        self.kal_Q = 1
        self.kal_R = 1
        self.isCali = (self.isCali_w or self.isCali_a)
        self.__Connector = None
        self.__portName = portName
        self.__baudRate = baudRate
        self.__isRun = True
        # self.__isCali = False
        self.__callBack = None
        self.__crcFail = 0
        self.arrayNum = 10
        self.__datacnt = 0
        self.__gpstime_old = 0
        self.__debug = debug_en
        self.__old_imudata = {k: (-1,) * len(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(1) for k in set(IMU_DATA_STRUCTURE)}
        # print(not __name__ == "__main__")

    # class constructor

    def __del__(self):
        print("class memsImuReader's destructor called!")

    # End of destructor

    @property
    def sf_a(self):
        return self.__sf_a

    @sf_a.setter
    def sf_a(self, value):
        self.__sf_a = value
        # print("act.sf_a: ", self.__sf_a)

    @property
    def sf_b(self):
        return self.__sf_b

    @sf_b.setter
    def sf_b(self, value):
        self.__sf_b = value
        # print("act.sf_b: ", self.__sf_b)

    @property
    def isKal(self):
        return self.__isKal

    @isKal.setter
    def isKal(self, en):
        self.__isKal = en
        logger.info("act.isKal: %s", self.isKal)

    @property
    def kal_Q(self):
        return self.__kal_Q

    @kal_Q.setter
    def kal_Q(self, Q):
        self.__kal_Q = Q
        self.nano33_wz_kal.kal_Q = self.kal_Q
        # self.pig_wz_kal.kal_Q = self.kal_Q

    @property
    def kal_R(self):
        return self.__kal_R

    @kal_R.setter
    def kal_R(self, R):
        self.__kal_R = R
        self.nano33_wz_kal.kal_R = self.kal_R
        # self.pig_wz_kal.kal_R = self.kal_R

    @property
    def dataRate(self):
        return self.__dataRate

    @dataRate.setter
    def dataRate(self, val):
        self.__dataRate = val

    @property
    def date_type(self):
        return self.__date_type

    @date_type.setter
    def date_type(self, type):
        self.__date_type = type

    @property
    def isRun(self):
        return self.__isRun

    # End of memsImuReader::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag

    # End of ImuReader::isRun(setter)

    @property
    def isCali(self):
        return self.__isCali

    # End of memsImuReader::isCali(getter)

    @isCali.setter
    def isCali(self, isFlag):
        self.__isCali = isFlag
        # print("self.__isCali: ", self.__isCali)

    # End of ImuReader::isCali(setter)

    @property
    def isCali_w(self):
        return self.__isCali_w

    # End of memsImuReader::isCali_w(getter)

    @isCali_w.setter
    def isCali_w(self, isFlag):
        self.__isCali_w = bool(int(isFlag))
        self.isCali = (self.isCali_w or self.isCali_a)

    # End of ImuReader::isCali_w(setter)

    @property
    def isCali_a(self):
        return self.__isCali_a

    # End of memsImuReader::isCali_a(getter)

    @isCali_a.setter
    def isCali_a(self, isFlag):
        self.__isCali_a = bool(int(isFlag))
        self.isCali = (self.isCali_w or self.isCali_a)

    # End of ImuReader::isCali_a(setter)

    def writeImuCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.__Connector.write(data)
        cmn.wait_ms(150)

    # End of memsImuReader::writeImuCmd

    def connect(self, port, portName, baudRate):
        self.__Connector = port
        port.portName = portName
        port.baudRate = baudRate
        is_open = self.__Connector.connect()
        return is_open

    # End of memsImuReader::connectIMU

    def disconnect(self):
        is_open = self.__Connector.disconnect()
        return is_open

    # End of memsImuReader::disconnectIMU

    def readIMU(self):
        self.writeImuCmd(7, 1)

    def stopIMU(self):
        self.writeImuCmd(7, 4)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
        dataPacket = getData.getdataPacket(self.__Connector, head, 34)
        NANO_WX, NANO_WY, NANO_WZ, \
        NANO_AX, NANO_AY, NANO_AZ = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX,
                                                   sf_xlm=SENS_NANO33_AXLM_4G,
                                                   sf_gyro=SENS_NANO33_GYRO_250)
        ADXL_AX, ADXL_AY, ADXL_AZ = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX,
                                                    sf=SENS_ADXL355_8G)
        GPS_DATE, GPS_TIME, valid = cmn.readGPS(dataPacket, EN=1, PRINT=0, POS_data=POS_DATE)
        if not self.isCali:
            if self.isKal:
                NANO_WZ = self.nano33_wz_kal.update(NANO_WZ)
        is_gpstime_renew = (GPS_TIME != self.__gpstime_old)

        t = time.perf_counter()
        gps_still_alive = is_gpstime_renew & valid
        # print('valid: ', valid)
        # self.__datacnt += 1
        # if bool(gps_still_alive):
        #     self.__datacnt = 0
        #     self.__carry_ms = 0
        #     self.__carry_ss = 0
        #     self.__carry_mm = 0
        # print(self.__gpstime_old, GPS_TIME, is_gpstime_renew, valid, gps_still_alive)
        # self.__gpstime_old = GPS_TIME
        gps_yy = int(GPS_DATE % 100 + 2000)
        gps_MM = int((GPS_DATE * 1e-2) % 100)
        gps_dd = int(GPS_DATE * 1e-4)
        gps_hh = int(GPS_TIME * 1e-6)
        gps_mm = int((GPS_TIME * 1e-4) % 100)
        gps_ss = int((GPS_TIME * 1e-2) % 100)
        gps_ms = int(self.__datacnt * 1e3 / self.dataRate)
        # print(gps_ms)
        if gps_ms >= 1000:
            self.__carry_ms += 1
            self.__datacnt = 0
        if self.__carry_ms == 60:
            self.__carry_ss += 1
            self.__carry_ms = 0
        if self.__carry_ss == 60:
            self.__carry_mm += 1
            self.__carry_ss = 0
        if bool(gps_still_alive):
            self.__datacnt = 0
            self.__carry_ms = 0
            self.__carry_ss = 0
            self.__carry_mm = 0
        self.__datacnt += 1
        self.__gpstime_old = GPS_TIME
        # print(gps_yy, gps_MM, gps_dd, gps_hh, gps_mm, gps_ss, self.__datacnt)
        gps_ss += self.__carry_ms
        # gps_ms = (gps_ss - int(gps_ss))*1e3
        gps_mm += self.__carry_ss
        gps_hh += self.__carry_mm
        imudata = {"NANO33_WX": NANO_WX, "NANO33_WY": NANO_WY, "NANO33_WZ": NANO_WZ,
                   "ADXL_AX": NANO_AX, "ADXL_AY": ADXL_AY, "ADXL_AZ": ADXL_AZ, "TIME": t,
                   "NANO33_AX": NANO_AX, "NANO33_AY": NANO_AY, "NANO33_AZ": NANO_AZ,
                   'YEAR': gps_yy, 'MON': gps_MM, 'DAY': gps_dd, 'HOUR': gps_hh,
                   'MIN': gps_mm, 'SEC': gps_ss, 'mSEC': gps_ms,
                   'DATA_CNT': self.__datacnt, 'GPS_ALIVE': gps_still_alive
                   }
        # print('valid: ', bool(valid))

        return dataPacket, imudata

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def do_cali(self, dictContainer, cali_times):
        if self.isCali:
            temp = {k: np.zeros(1) for k in set(IMU_DATA_STRUCTURE)}
            cmn.print_debug('temp before: %s' % temp, PRINT_DEBUG)
            logger.info("---calibrating offset start-----")
            for i in range(cali_times):
                dataPacket, imudata = self.getImuData()
                cmn.print_debug('imudata: %s' % imudata, PRINT_DEBUG)
                temp = cmn.dictOperation(temp, imudata, "ADD", IMU_DATA_STRUCTURE)
            cmn.print_debug('temp after: %s' % temp, PRINT_DEBUG)
            temp = {k: temp.get(k) / cali_times for k in set(self.__imuoffset)}
            logger.info("---calibrating offset stop-----")
            self.isCali = False
            self.__datacnt = 0
            return temp
        else:
            return dictContainer

    def run(self):
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        while True:
            if not self.isRun:
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                self.__datacnt = 0
                break
            # End of if-condition
            cmn.print_debug('self.__imuoffset before: %s' % self.__imuoffset, PRINT_DEBUG)
            self.__imuoffset = self.do_cali(self.__imuoffset, 100)
            cmn.print_debug('self.__imuoffset after: %s' % self.__imuoffset, PRINT_DEBUG)

            imudataArray = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}
            # gpsdataArray = {k: np.empty(0) for k in set(GPS_DATA_STRUCTURE)}

            for i in range(self.arrayNum):
                input_buf = self.readInputBuffer()
                self.buffer_qt.emit(input_buf)
                # while self.__Connector.readInputBuffer() < self.arrayNum * 10:
                while not self.__Connector.readInputBuffer():
                    # print(self.__Connector.readInputBuffer())
                    # print("No input data!")
                    # cmn.wait_ms(500)
                    pass
                t1 = time.perf_counter()

                dataPacket, imudata = self.getImuData()
                t2 = time.perf_counter()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                t3 = time.perf_counter()
                # err correction
                imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
                t4 = time.perf_counter()
                # imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE)
                # print(imudata)
                ''' PC time'''
                currentDateAndTime = datetime.now()
                yy = currentDateAndTime.year
                MM = currentDateAndTime.month
                dd = currentDateAndTime.day
                hh = currentDateAndTime.hour
                mm = currentDateAndTime.minute
                ss = currentDateAndTime.second
                ms = int(currentDateAndTime.microsecond * 1e-3)
                if self.date_type == 'PC':
                    imudata['YEAR'] = yy
                    imudata['MON'] = MM
                    imudata['DAY'] = dd
                    imudata['HOUR'] = hh
                    imudata['MIN'] = mm
                    imudata['SEC'] = ss
                    imudata['mSEC'] = ms
                ''' end of PC time'''
                imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
                imudataArray["ADXL_AX"] = np.append(imudataArray["ADXL_AX"], imudata["ADXL_AX"])
                imudataArray["ADXL_AY"] = np.append(imudataArray["ADXL_AY"], imudata["ADXL_AY"])
                imudataArray["ADXL_AZ"] = np.append(imudataArray["ADXL_AZ"], imudata["ADXL_AZ"])
                imudataArray["NANO33_WX"] = np.append(imudataArray["NANO33_WX"], imudata["NANO33_WX"])
                imudataArray["NANO33_WY"] = np.append(imudataArray["NANO33_WY"], imudata["NANO33_WY"])
                imudataArray["NANO33_WZ"] = np.append(imudataArray["NANO33_WZ"], imudata["NANO33_WZ"])
                imudataArray["NANO33_AX"] = np.append(imudataArray["NANO33_AX"], imudata["NANO33_AX"])
                imudataArray["NANO33_AY"] = np.append(imudataArray["NANO33_AY"], imudata["NANO33_AY"])
                imudataArray["NANO33_AZ"] = np.append(imudataArray["NANO33_AZ"], imudata["NANO33_AZ"])
                imudataArray["YEAR"] = np.append(imudataArray["YEAR"], imudata["YEAR"])
                imudataArray["MON"] = np.append(imudataArray["MON"], imudata["MON"])
                imudataArray["DAY"] = np.append(imudataArray["DAY"], imudata["DAY"])
                imudataArray["HOUR"] = np.append(imudataArray["HOUR"], imudata["HOUR"])
                imudataArray["MIN"] = np.append(imudataArray["MIN"], imudata["MIN"])
                imudataArray["SEC"] = np.append(imudataArray["SEC"], imudata["SEC"])
                imudataArray["mSEC"] = np.append(imudataArray["mSEC"], imudata["mSEC"])
                imudataArray["DATA_CNT"] = np.append(imudataArray["DATA_CNT"], imudata["DATA_CNT"])
                imudataArray["GPS_ALIVE"] = np.append(imudataArray["GPS_ALIVE"], imudata["GPS_ALIVE"])
                # print(imudata["GPS_YEAR"], imudata["GPS_MON"], imudata["GPS_DAY"], imudata["GPS_HOUR"],
                #       imudata["GPS_MIN"], imudata["GPS_SEC"], imudata["DATA_CNT"])
                t5 = time.perf_counter()

                debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                             + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                             + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)

            # end of for loop

            imudataArray["TIME"] = imudataArray["TIME"] - t0

            self.offset_setting(self.__imuoffset)
            imudataArray = cmn.dictOperation(imudataArray, self.__imuoffset, "SUB", IMU_DATA_STRUCTURE)

            if self.__callBack is not None:
                self.__callBack(imudataArray)

            if not __name__ == "__main__":
                self.imudata_qt.emit(imudataArray)
            # print(imudataArray)

        # end of while loop

    # End of memsImuReader::run

    def offset_setting(self, imuoffset):
        imuoffset["TIME"] = [0]
        imuoffset["YEAR"] = [0]
        imuoffset["MON"] = [0]
        imuoffset["DAY"] = [0]
        imuoffset["HOUR"] = [0]
        imuoffset["MIN"] = [0]
        imuoffset["SEC"] = [0]
        imuoffset["mSEC"] = [0]
        imuoffset["GPS_ALIVE"] = [0]
        imuoffset["DATA_CNT"] = [0]
        if not self.isCali_w:
            imuoffset["NANO33_WX"] = [0]
            imuoffset["NANO33_WY"] = [0]
            imuoffset["NANO33_WZ"] = [0]
        if not self.isCali_a:
            imuoffset["ADXL_AX"] = [0]
            imuoffset["ADXL_AY"] = [0]
            imuoffset["ADXL_AZ"] = [0]
            imuoffset["NANO33_AX"] = [0]
            imuoffset["NANO33_AY"] = [0]
            imuoffset["NANO33_AZ"] = [0]


def myCallBack(imudata):
    global old
    new = time.perf_counter_ns()
    # print(imudata)
    # wx = imudata["NANO33_W"][0]
    # wy = imudata["NANO33_W"][1]
    # wz = imudata["NANO33_W"][2]
    # ax = imudata["ADXL_A"][0]
    # ay = imudata["ADXL_A"][1]
    # az = imudata["ADXL_A"][2]
    # t = imudata["TIME"][0]
    # print("%.5f %.5f  %.5f  %.5f  %.5f  %.5f  %.5f" % (t, wx, wy, wz, ax, ay, az))
    # print(imudata["TIME"], imudata["NANO33_W"], imudata["ADXL_A"])
    old = new


if __name__ == "__main__":
    ser = Connector()
    myImu = memsImuReader(debug_en=False)
    myImu.arrayNum = 2
    myImu.setCallback(myCallBack)
    myImu.isCali = True
    myImu.connect(ser, "COM5", 230400)
    myImu.readIMU()
    myImu.isRun = True
    myImu.start()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.stopIMU()
        myImu.disconnect()
        myImu.wait()
        print('KeyboardInterrupt success')
