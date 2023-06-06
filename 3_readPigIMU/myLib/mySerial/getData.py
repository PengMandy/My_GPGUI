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
import myLib.common as cmn
import sys
PRINT_DEBUG = 0

def alignHeader_4B(comportObj, header):
    datain = comportObj.readBinaryList(4)
    while 1:
        if datain == header:
            return datain
        else:
            try:
                datain[0] = datain[1]
                datain[1] = datain[2]
                datain[2] = datain[3]
                datain[3] = comportObj.readBinaryList(1)[0]
            # except IndexError:
            #     logger.error('IndexError: alignHeader_4B')
            #     sys.exit()
            #     break
            except:
                logger.error('alignHeader_4B Error')
                sys.exit()
                break

            # print(datain)
# End of alignHeader_4B

def alignHeader_7B(comportObj, header):
    datain = comportObj.readBinaryList(7)
    while 1:
        if datain == header:
            return datain
        else:
            try:
                datain[0] = datain[1]
                datain[1] = datain[2]
                datain[2] = datain[3]
                datain[3] = datain[4]
                datain[4] = datain[5]
                datain[5] = datain[6]
                datain[6] = comportObj.readBinaryList(1)[0]
                # print(datain, header, datain==header)
            except IndexError:
                logger.error('IndexError: alignHeader_7B')
                sys.exit()
                break

def getdataPacket(comportObj, head, rbytes=25):
    rdata = comportObj.readBinaryList(rbytes)
    imuPacket = head + rdata
    return imuPacket
# End of getdataPacket


if __name__ == "__main__":
    from Connector import Connector
    import time

    HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
    ser = Connector("COM5")
    old_time = time.perf_counter()
    ser.connect()
    ser.write([5, 0, 0, 0, 1])
    try:
        while 1:
            ser.readInputBuffer()
            head = alignHeader_4B(ser, HEADER_KVH)
            dataPacket = getdataPacket(ser, head, 25)
            print(dataPacket)
            print("%f\n" % ((time.perf_counter() - old_time) * 1e6))
            old_time = time.perf_counter()

    except KeyboardInterrupt:
        ser.write([5, 0, 0, 0, 4])
        ser.disconnect()
    pass
