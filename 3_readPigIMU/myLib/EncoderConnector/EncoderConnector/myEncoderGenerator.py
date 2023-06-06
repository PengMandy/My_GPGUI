import socket
import time
from threading import Thread
from random import uniform

class myEncoderGenerator(Thread):
    """
    Description:
    =============================================================
    This class will generate fake datum to send via socket for 
    testing this project.

    ------------------------------------
    Programmer:     HONG-CING HUANG

    Date:       2022.03.07
    """

    Max_Encoder_Step = 6000

    def __init__(self, strIP:str="127.0.0.1", iPort:int=9000, fUpdateTime:float=0.5) -> None:
        """
        Description:
        ========================================================
        Initialize the object of this class.

        Args:
        ========================================================
        - strIP:        ptype: str, the server IP
        - iPort:        ptype: int, the server port
        - fUpdateTime:  ptype: float, the updatate time to send datum to client

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        super().__init__()

        self.__m_strIP = strIP
        self.__m_iPort = iPort
        self.__m_fUpdateTime = fUpdateTime
        self.__m_isRun = True
        self.__m_iSequence = 0
        self.__m_iStep = 0
        self.__m_fDistance = 0.0

        self.__m_oServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # End of constructor

    @property
    def isRun(self):
        """
        Description:
        =======================================================
        This flag can control this class to run or not.

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        return self.__m_isRun
    # End of myEncoderGenerator::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag:bool):
        self.__m_isRun = isFlag
    # End of myEncoderGenerator::isRun(setter)

    def __sendClient(self, oClient:socket.socket):
        """
        Description:
        =======================================================
        Send datum to the client until the client abort the
        connection.

        Args:
        =======================================================
        - oClient:  ptype: socket.socket, this object can send datum via socket

        Returns:
        =======================================================
        - rtype: void

        ------------------------------------
        Programmer:     HONG-CING HUANG

        Date:       2022.03.07
        """
        while True:
            if False == self.isRun:
                break
            # End of if-condition

            strData = "%d,%d,%.6f,%.6f,%.6f,%.6f" %(self.__m_iSequence, self.__m_iStep, 
                self.__m_fDistance, uniform(0.0, 1000.0), uniform(0.0, 100.0), 
                uniform(0.0, 50.0))

            print("\x1b[32mServer send: %s\x1b[0m" %(strData))
            strData += "\r\n"
            oClient.send(strData.encode("utf-8"))

            self.__m_iSequence += 1
            self.__m_iStep = (self.__m_iStep + 1) % myEncoderGenerator.Max_Encoder_Step
            self.__m_fDistance += uniform(0.0, 10.0)

            time.sleep(self.__m_fUpdateTime)
        # End of while-loop
    # End of myEncoderGenerator::connectClient

    def run(self) -> None:
        self.__m_oServer.bind((self.__m_strIP, self.__m_iPort))
        self.__m_oServer.listen(5)

        print("\x1b[32mServer is ready to connect: (%s, %d)\x1b[0m" %(self.__m_strIP, self.__m_iPort))

        while True:
            if False == self.isRun:
                break
            # End of if-condition

            oClient, addr = self.__m_oServer.accept()
            print("\x1b[32mServer connects client: %s\x1b[0m" %(str(addr)))
            self.__sendClient(oClient)
        # End of while-loop

        self.__m_oServer.close()
        print("\x1b[32mServer closed connection!\x1b[0m")
    # End of myEncoderGenerator::run
# End of myEncoderGenerator