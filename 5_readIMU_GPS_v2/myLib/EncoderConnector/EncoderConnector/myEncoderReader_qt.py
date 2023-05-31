import sys
sys.path.append('../../../')
from myLib.EncoderConnector.EncoderConnector import myEncoderConnector
from PyQt5.QtCore import QThread, pyqtSignal

import time
from threading import Thread


class myEncoderReader(QThread):
    speed_qt = pyqtSignal(object)
    """
    Description:
    ===============================================================
    This class can read datum from NI to get the status of encoder.

    ------------------------------------
    Programmer:     HONG-CING HUANG

    Date:       2022.03.07
    """

    def __init__(self, strIP: str = "192.168.1.178", iPort: int = 9000,
                 fUpdateTime: float = 5e-3) -> None:
        """
        Description:
        =======================================================
        Initialize the object of this class.

        Args:
        =======================================================
        - strIP:        ptype: str, the server IP
        - iPort:        ptype: int, the server port
        - fUpdateTime:  ptype: float, the update time to obtain status of encoder from server

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        super().__init__()

        self.__m_oEncoderConnector = myEncoderConnector.myEncoderConnector(strIP, iPort)
        self.__m_fUpdateTime = fUpdateTime
        self.__m_isRun = True
        self.__m_oCallBacker = None

    # End of constructor

    @property
    def isRun(self):
        """
        Description:
        =====================================================
        This flag can control this class to run or not.

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        return self.__m_isRun

    # End of myEncoderReader::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag: bool):
        self.__m_isRun = isFlag

    #  End of myEncoderReader:isRun(setter)

    def setCallback(self, callback):
        """
        Description:
        ======================================================
        Set the callback fucntion.

        Args:
        ======================================================
        - callback: ptype: fuction, this argument is a callback fucntion

        Returns:
        ======================================================
        - rtype: void

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.08
        """
        self.__m_oCallBacker = callback

    # End of myEncoderReader::setCallback

    def connectServer(self):
        """
        Description:
        =======================================================
        Connect server.

        Args:
        =======================================================
        - no args

        Returns:
        =======================================================
        - rtype: void

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        self.__m_oEncoderConnector.connect()

    # End of myEncoderReader::connectServer

    def run(self) -> None:
        fPreUpdateTime = time.perf_counter()
        while True:
            if False == self.isRun:
                break
            # End of if-condition
            strSequence, iStep, fDistance, fEncoderSpeed, fVehicleSpeed, fVehicleAcceleration = self.__m_oEncoderConnector.obtainStatus()

            if time.perf_counter() - fPreUpdateTime >= self.__m_fUpdateTime:
                dctStatus = {}
                dctStatus["Sequence"] = strSequence
                dctStatus["Step"] = iStep
                dctStatus["Distance"] = fDistance
                dctStatus["EncoderSpeed"] = fEncoderSpeed
                dctStatus["VehicleSpeed"] = fVehicleSpeed
                dctStatus["VehicleAcceleration"] = fVehicleAcceleration
                self.speed_qt.emit(fVehicleSpeed)
                if not self.__m_oCallBacker is None:
                    self.__m_oCallBacker(dctStatus)
                # End of if-condition

                fPreUpdateTime = time.perf_counter()
            # End of if-condition
        # End of while-loop

        self.__m_oEncoderConnector.close()
    # End of myEncoderReader::run
# End of class myEncoderReader
