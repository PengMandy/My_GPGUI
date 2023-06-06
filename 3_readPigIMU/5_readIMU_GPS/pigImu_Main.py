""" ####### log stuff creation, always on the top ########  """
import os
import builtins
import yaml
import logging.config

LOG_PATH = './logs/'
LOGGER_NAME = 'main'
builtins.LOGGER_NAME = LOGGER_NAME
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
f_log = open('log_config.yaml', 'r', encoding='utf-8')
config = yaml.safe_load(f_log)
logging.config.dictConfig(config)
logger = logging.getLogger(LOGGER_NAME)
f_log.close()
logger.info('create log stuff done, ')
logger.info('process start')
""" ####### end of log stuff creation ########  """

import sys

sys.path.append("../")
from myLib import common as cmn
from myLib.myGui.mygui_serial import *
import time
from myLib.mySerial.Connector import Connector
from myLib.myGui.pig_parameters_widget import pig_parameters_widget
from myLib.myGui.pig_parameters_widget import CMD_FOG_TIMER_RST
from myLib.myGui.pig_menu_manager import pig_menu_manager
from myLib.myGui import analysis_Allan, analysis_TimingPlot
from myLib.myGui import autoSave
from PyQt5.QtWidgets import *
from pigImu_Widget import pigImuWidget as TOP
from pigImuReader_gps import pigImuReader as ACTION
from pigImuReader_gps import IMU_DATA_STRUCTURE
import numpy as np

PRINT_DEBUG = 0


class mainWindow(QMainWindow):
    is_port_open_qt = pyqtSignal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.press_stop = False
        self.resize(1450, 800)
        self.pig_parameter_widget = None
        self.__portName = None
        self.setWindowTitle("Aegiverse IMU GUI")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.__skipcnt = 0
        self.top = TOP()
        self.act = ACTION()
        # self.imudata_file = cmn.data_manager(fnum=0)
        self.imudata_file_auto = autoSave.atSave_PC_v2(fnum=0)
        self.pig_cali_menu = calibrationBlock()
        self.act.isCali = True
        self.menu = self.menuBar()
        self.pig_menu = pig_menu_manager(self.menu, self)
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['wx', 'wy', 'wz', 'ax', 'ay', 'az'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['wx', 'wy', 'wz', 'ax', 'ay', 'az', 'yy', 'MM', 'dd', 'hh', 'mm', 'ss', 'ms'])
        self.linkfunction()
        self.act.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()

        self.__debug = debug_en
        self.t_start = time.perf_counter()
        self.act.date_type = self.top.date_rb.btn_status

    def mainUI(self):
        self.setCentralWidget(self.top)

    def linkfunction(self):
        # usb connection
        self.top.usb.bt_update.clicked.connect(self.updateComPort)
        self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
        self.top.usb.bt_connect.clicked.connect(self.connect)
        self.top.usb.bt_disconnect.clicked.connect(self.disconnect)
        # bt connection
        self.top.read_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.stop)
        # rb connection
        self.top.kal_filter_rb.toggled.connect(lambda: self.update_kalFilter_en(self.top.kal_filter_rb))
        # pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        self.act.buffer_qt.connect(self.printBuffer)
        self.is_port_open_qt.connect(self.is_port_open_status_manager)
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_parameters,
                                              self.show_calibration_menu,
                                              self.show_plot_data_menu,
                                              self.show_cal_allan_menu
                                              ])
        # file name le
        self.top.save_block.le_filename.editingFinished.connect(
            lambda: self.file_name_le_connect(self.top.save_block.le_filename))

    def file_name_le_connect(self, obj):
        cmn.print_debug('file name: %s' % obj.text(), PRINT_DEBUG)
        filename = obj.text() + self.top.save_block.le_ext.text()
        self.analysis_timing_plot.pbar.set_filename_ext(filename)
        self.analysis_allan.pbar.set_filename_ext(filename)

    def show_parameters(self):
        self.pig_parameter_widget.show()

    def show_calibration_menu(self):
        self.pig_cali_menu.show()

    def show_plot_data_menu(self):
        self.analysis_timing_plot.show()

    def show_cal_allan_menu(self):
        self.analysis_allan.show()

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

    def printGPS_Time(self, val):
        self.top.gpstime_lb.lb.setText(val)

    def printPdTemperature(self, val):
        if (time.perf_counter() - self.t_start) > 0.5:
            self.top.pd_temp_lb.lb.setText(str(val))
            self.t_start = time.perf_counter()

    def printUpdateRate(self, t_list):
        update_rate = round(((t_list[-1] - t_list[0]) / (len(t_list) - 1)) ** -1, 1)
        self.top.data_rate_lb.lb.setText(str(update_rate))

    def updateComPort(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.addPortItems(portNum, portList)

    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        is_port_open = self.act.connect(self.__connector, self.__portName, 230400)
        self.is_port_open_qt.emit(is_port_open)
        self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
        self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act

    def disconnect(self):
        is_port_open = self.act.disconnect()
        self.is_port_open_qt.emit(is_port_open)

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetFPGATimer(self):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1)

    def start(self):
        self.resetFPGATimer()
        self.act.readIMU()
        self.act.isRun = True
        self.press_stop = False
        self.act.start()
        file_name = self.top.save_block.le_filename.text()
        # self.imudata_file.name = file_name
        # self.imudata_file.open(self.top.save_block.rb.isChecked())
        # self.imudata_file.write_line('time,fog,wx,wy,wz,ax,ay,az,T')
        self.imudata_file_auto.data_path = file_name
        self.imudata_file_auto.start = True
        self.imudata_file_auto.create_data_folder(self.top.save_block.rb.isChecked())
        self.imudata_file_auto.auto_create_folder(self.top.save_block.rb.isChecked())
        # self.imudata_file_auto.write_line('time,wx,wy,wz,ax,ay,az,yy,MM,dd,hh,mm,ss')

    def stop(self):
        self.resetFPGATimer()
        self.act.isRun = False
        # self.top.save_block.rb.setChecked(False)
        # self.imudata_file.close()
        if self.top.save_block.rb.isChecked():
            self.imudata_file_auto.close_hour_folder()
            self.imudata_file_auto.reset_hh_reg()
            self.top.save_block.rb.setChecked(False)
        self.press_stop = True
        print('press stop')

    @property
    def press_stop(self):
        return self.__stop

    @press_stop.setter
    def press_stop(self, stop):
        self.__stop = stop

    def collectData(self, imudata):
        if not self.press_stop:
            self.act.date_type = self.top.date_rb.btn_status
            # print('collectData: ', imudata)
            input_buf = self.act.readInputBuffer()
            t0 = time.perf_counter()
            # imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
            self.printPdTemperature(imudata["PD_TEMP"][0])
            t1 = time.perf_counter()
            # self.imudata = cmn.dictOperation(self.imudata, imudata, "APPEND", IMU_DATA_STRUCTURE)
            self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"])
            self.imudata["ADXL_AX"] = np.append(self.imudata["ADXL_AX"], imudata["ADXL_AX"])
            self.imudata["ADXL_AY"] = np.append(self.imudata["ADXL_AY"], imudata["ADXL_AY"])
            self.imudata["ADXL_AZ"] = np.append(self.imudata["ADXL_AZ"], imudata["ADXL_AZ"])
            self.imudata["NANO33_WX"] = np.append(self.imudata["NANO33_WX"], imudata["NANO33_WX"])
            self.imudata["NANO33_WY"] = np.append(self.imudata["NANO33_WY"], imudata["NANO33_WY"])
            self.imudata["NANO33_WZ"] = np.append(self.imudata["NANO33_WZ"], imudata["NANO33_WZ"])
            self.imudata["PIG_WZ"] = np.append(self.imudata["PIG_WZ"], imudata["PIG_WZ"])
            self.imudata["PIG_ERR"] = np.append(self.imudata["PIG_ERR"], imudata["PIG_ERR"])
            self.imudata["PD_TEMP"] = np.append(self.imudata["PD_TEMP"], imudata["PD_TEMP"])
            # print(len(self.imudata["TIME"]), end=", ")
            if len(self.imudata["TIME"]) > 1000:
                self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["ADXL_AX"] = self.imudata["ADXL_AX"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["ADXL_AY"] = self.imudata["ADXL_AY"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["ADXL_AZ"] = self.imudata["ADXL_AZ"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["NANO33_WX"] = self.imudata["NANO33_WX"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["NANO33_WY"] = self.imudata["NANO33_WY"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["NANO33_WZ"] = self.imudata["NANO33_WZ"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["PIG_WZ"] = self.imudata["PIG_WZ"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["PIG_ERR"] = self.imudata["PIG_ERR"][self.act.arrayNum:self.act.arrayNum + 1000]
                self.imudata["PD_TEMP"] = self.imudata["PD_TEMP"][self.act.arrayNum:self.act.arrayNum + 1000]
            t2 = time.perf_counter()
            if self.__skipcnt < 10:
                self.__skipcnt += 1
                # print('self.__skipcnt: ', self.__skipcnt)
                return
            self.printUpdateRate(imudata["TIME"])
            debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                         + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
            cmn.print_debug(debug_info, self.__debug)

            # print(imudata["PIG_WZ"])
            datalist = [imudata["TIME"], imudata["PIG_WZ"], imudata["PIG_WZ"], imudata["PIG_WZ"]
                , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]
                , imudata['YEAR'], imudata['MON'], imudata['DAY'], imudata['HOUR']
                , imudata['MIN'], imudata['SEC'], imudata['mSEC']]
            data_fmt = "%.4f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%d,%d,%d,%d,%d,%d,%d"
            gps_time = '%d/%d/%d %d:%d:%d.%d' % (imudata['YEAR'][0], imudata['MON'][0], imudata['DAY'][0],
                                                 imudata['HOUR'][0], imudata['MIN'][0], imudata['SEC'][0],
                                                 imudata['mSEC'][0])
            self.printGPS_Time(gps_time)
            self.imudata_file_auto.saveData(datalist, data_fmt)
            self.imudata_file_auto.auto_create_folder(self.top.save_block.rb.isChecked())
            # self.imudata_file.saveData(datalist, data_fmt)
            self.plotdata(self.imudata)

            # print(len(self.imudata["TIME"]))

    def plotdata(self, imudata):
        # print('plotdata: ', imudata['TIME'])
        if self.top.plot1_unit_rb.btn_status == 'dph':
            factor = 3600
        else:
            factor = 1

        if self.top.plot1_showWz_cb.cb_1.isChecked():
            self.top.plot1.ax1.setData(imudata["TIME"], imudata["PIG_WZ"] * factor)
            # self.top.plot1.ax1.setData(imudata["TIME"], imudata["PIG_ERR"])
        else:
            self.top.plot1.ax1.clear()
        if self.top.plot1_showWz_cb.cb_2.isChecked():
            self.top.plot1.ax2.setData(imudata["TIME"], imudata["NANO33_WZ"] * factor)
        else:
            self.top.plot1.ax2.clear()

        self.top.plot2.ax.setData(imudata["ADXL_AX"])
        self.top.plot3.ax.setData(imudata["ADXL_AY"])
        self.top.plot4.ax.setData(imudata["ADXL_AZ"])
        self.top.plot5.ax.setData(imudata["NANO33_WX"])
        self.top.plot6.ax.setData(imudata["NANO33_WY"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
