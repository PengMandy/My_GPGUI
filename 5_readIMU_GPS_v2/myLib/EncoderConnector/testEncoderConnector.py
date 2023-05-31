from EncoderConnector import myEncoderConnector
import traceback
import time

def testEncoderConnector():
    """
    Description:
    ======================================
    Demo to use the class myEncoderConnector

    Args:
    ======================================
    - no args

    Returns:
    ======================================
    - rtype: void
    """
    oEncoderConnector = myEncoderConnector()

    oEncoderConnector.connect()

    fStartTime = time.perf_counter()
    while True:
        try:
            strSequence, iEncoderStep, fDistance, fEncoderSpeed, fVehicleSpeed, fVehicleAcceleration = oEncoderConnector.obtainStatus()
            print("Obtain Status: %s, %d, %.6f, %.6f, %.6f, %.6f" %(strSequence, iEncoderStep, fDistance, fEncoderSpeed, fVehicleSpeed, fVehicleAcceleration))

            if time.perf_counter() - fStartTime >= 30.0:
                break
            # End of if-condition
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
        # End of try-catch
    # End of while-loop

    oEncoderConnector.close()
# End of testEncoderConnector

def main():
    testEncoderConnector()
# End of main

if "__main__" == __name__:
    main()
# End of if-condition