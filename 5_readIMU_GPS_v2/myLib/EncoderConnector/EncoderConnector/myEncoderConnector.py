import socket
from typing import Tuple

class myEncoderConnector:
    """
    Description:
    =============================================================
    This class can fetch daum from encoder via socket.

    ------------------------------------
    Programmer:     HONG-CING HUANG

    Date:       2022.03.04
    """
    def __init__(self, strIP:str="192.168.1.178", iPort:int=9000) -> None:
        """
        Description:
        ==========================================================
        Initialize the object of this class.

        Args:
        ==========================================================
        - strIP:        ptype: str, the server IP
        - iPort:        ptype: int, the server port
        
        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.04
        """

        self.__m_strIP = strIP
        self.__m_iPort = iPort
        self.__m_iBufferSize = 1
        
        self.__m_oConnector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # End of constructor

    def connect(self):
        """
        Description:
        =========================================================
        Connect server to obtain datum from encoder.

        Args:
        =========================================================
        - no args

        Returns:
        =========================================================
        - rtype: void

        Exception:
        =========================================================
        This method will issue exception if fails to connect server.

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        self.__m_oConnector.connect((self.__m_strIP, self.__m_iPort))
    # End of myEncoderConnector::connect

    def close(self):
        """
        Description:
        =======================================================
        Close the connection.

        Args:
        =======================================================
        - no args

        Return:
        =======================================================
        - rtype: void

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        self.__m_oConnector.close()
    # End of myEncoderConnector::close

    def __receiveData(self) -> str:
        """
        Description:
        ================================================
        Receive a data from server.

        Args:
        ================================================
        - no args

        Returns:
        ================================================
        - rtype: str, return the raw data from server

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.09
        """
        strRawData = ""
        while True:
            bReceiveData = self.__m_oConnector.recv(self.__m_iBufferSize)
            strReceiveData = bReceiveData.decode("utf-8")
            strRawData += strReceiveData
            if "\r" in strRawData:
                break
            # End of  if-condition
        # End of while-loop

        return strRawData.strip()
    # End of myEncoderConnector::receiveData

    def obtainStatus(self) -> Tuple[str, int, float, float, float, float]:
        """
        Description:
        ========================================================
        Obtain encoder datum from server.

        Args:
        ========================================================
        - no args

        Returns:
        ========================================================
        - rtype: str, the sequence number of the datum from server
        - rtype: int, the step of encoder
        - rtype: float, the moved distance, and the unit is meter
        - rtype: float, the speed of encoder, and the unit is step/second
        - rtype: float, the vehicle speed, and the unit is KM/Hr
        - rtype: float, the acceleration of the vehicle, and the unit is KM/sec^2

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        strRawData = self.__receiveData()
        vstrData = strRawData.split(",")

        strSequence = vstrData[0].strip()
        iEncoderStep = float(vstrData[1].strip())
        fDistance = float(vstrData[2].strip())
        fEncoderSpeed = float(vstrData[3].strip())
        fVehicleSpeed = float(vstrData[4].strip())
        fVehicleAcceleration = float(vstrData[5].strip())

        return strSequence, iEncoderStep, fDistance, fEncoderSpeed, fVehicleSpeed, fVehicleAcceleration
    # End of myEncoderConnector::obtainStatus
# End of class myEncoderConnector