from EncoderConnector import myEncoderReader
from EncoderConnector.myEncoderGenerator import myEncoderGenerator
import time
import os

def getStatus(dctStatus:dict):
    """
    Description:
    =========================================================
    This function is a callback function that obtains the
    status of encoder from the class myEncoderReader.

    Args:
    =========================================================
    - dctStatus:    ptype: dict, this argument can send the status of the encoder

    Returns:
    =========================================================
    - rtype: void
    """
    strSequence = dctStatus["Sequence"]
    iStep = dctStatus["Step"]
    fDistance = dctStatus["Distance"]
    fEncoderSpeed = dctStatus["EncoderSpeed"]
    fVehicleSpeed = dctStatus["VehicleSpeed"]
    fVehicleAcceleration = dctStatus["VehicleAcceleration"]

    print("Receive: %s, %d, %.6f, %.6f, %.6f, %.6f" %(strSequence, iStep, fDistance, fEncoderSpeed, fVehicleSpeed, fVehicleAcceleration))
# End of getStatus

def testFunction():
    """
    Description:
    ========================================================
    Test callback function.

    Args:
    ========================================================
    - no args

    Returns:
    ========================================================
    - rtype: void
    """
    oGenerator = myEncoderGenerator("127.0.0.1", fUpdateTime=0.25)
    oGenerator.start()

    oReader = myEncoderReader("127.0.0.1")
    oReader.setCallback(getStatus)
    oReader.connectServer()

    oReader.start()

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            oReader.isRun = False
            time.sleep(1)
            oGenerator.isRun = False
            time.sleep(1)
            break
        except:
            pass
        # End of try-catch
    # End of while-loop
        
    oReader.join()
    oGenerator.join()
# End of testCallback

def main():
    os.system("cls")    # clear terminal to print color words
    testFunction()
# End of main

if "__main__" == __name__:
    main()
# End of main