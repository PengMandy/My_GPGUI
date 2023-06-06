import time
import os
from threading import Thread
from EncoderConnector import myEncoderReader
from EncoderConnector.myEncoderGenerator import myEncoderGenerator

class myCallBack(Thread):
    """
    Description:
    ====================================================
    This class has a method as a callback fucntion to
    obtain the status of the encoder from the class 
    myEncoderReader.
    """
    def __init__(self) -> None:
        super().__init__()
        self.__m_strSequence = ""
        self.__m_iStep = 0
        self.__m_fDistance = 0.0
        self.__m_fEncoderSpeed = 0.0
        self.__m_fVehicleSpeed = 0.0
        self.__m_fVehicleAcceleration = 0.0
        self.__m_isSet = False
        self.__m_isRun = True
    # End of constructor

    @property
    def isRun(self):
        """
        Description:
        ================================================
        This flag can control this class to continue 
        running or not.
        """
        return self.__m_isRun
    # End of myCallBack::isRun

    @isRun.setter
    def isRun(self, isFlag:bool):
        self.__m_isRun = isFlag
    # End of myCallBack::isRun

    def setStatus(self, dctStatus:dict):
        """
        Description:
        ===============================================================
        This method is a callback function that can obtain the status
        of the encoder.

        Args:
        ===============================================================
        - dctStatus:    ptype: dict, this argument can receive the status of encoder

        Returns:
        ===============================================================
        - rtype: void
        """
        self.__m_strSequence = dctStatus["Sequence"]
        self.__m_iStep = dctStatus["Step"]
        self.__m_fDistance = dctStatus["Distance"]
        self.__m_fEncoderSpeed = dctStatus["EncoderSpeed"]
        self.__m_fVehicleSpeed = dctStatus["VehicleSpeed"]
        self.__m_fVehicleAcceleration = dctStatus["VehicleAcceleration"]
        self.__m_isSet = True
    # End of myCallBack::setStatus

    def run(self) -> None:
        while True:
            if False == self.isRun: 
                break
            # End of if-condition

            if True == self.__m_isSet:
                print("Callback get: %s, %d, %.6f, %.6f, %.6f, %.6f" %(
                    self.__m_strSequence, self.__m_iStep, self.__m_fDistance, self.__m_fEncoderSpeed, 
                    self.__m_fVehicleSpeed, self.__m_fVehicleAcceleration))
                
                self.__m_isSet = False
            # End of if-condition

            time.sleep(0.1)
        # End of while-loop
    # End of myCallBack::run
# End of class myCallBack

def testObjectOriented():
    """
    Description:
    ============================================================
    Test use object oriented to design callback function.

    Args:
    ============================================================
    - no args

    Returns:
    ============================================================
    - rtype: void
    """
    oGenerator = myEncoderGenerator("127.0.0.1", fUpdateTime=0.25)
    oGenerator.start()

    oCallBacker = myCallBack()
    oReader = myEncoderReader("127.0.0.1")
    oReader.setCallback(oCallBacker.setStatus)
    oReader.connectServer()

    oCallBacker.start()
    oReader.start()

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            oReader.isRun = False
            time.sleep(1)
            oGenerator.isRun = False
            time.sleep(1)
            oCallBacker.isRun = False
            time.sleep(1)
            break
        except:
            pass
        # End of try-catch
    # End of while-loop
        

    oCallBacker.join()
    oReader.join()
    oGenerator.join()
# End of testOO

def main():
    os.system("cls")    # clear terminal to print color words
    testObjectOriented()
# End of main

if "__main__" == __name__:
    main()
# End of main