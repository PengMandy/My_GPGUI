from EncoderConnector import myEncoderReader

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

def main():
    oReader = myEncoderReader()
    oReader.setCallback(getStatus)
    oReader.connectServer()
    oReader.start()
    oReader.join()
# End of main

if "__main__" == __name__:
    main()
# End of if-condition