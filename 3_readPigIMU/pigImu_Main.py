""" ####### log stuff creation, always on the top ########  """
import gc
import os
import builtins
import pathlib
from datetime import datetime

import serial
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
from myLib.myGui import analysis_Allan, analysis_TimingPlot, myRadioButton, autoSave
from PyQt5.QtWidgets import *
from pigImu_Widget import pigImuWidget as TOP
from pigImuReader import pigImuReader as ACTION
from pigImuReader import IMU_DATA_STRUCTURE
import numpy as np

PRINT_DEBUG = 0
OUTPUT_ONE_AXIS = True


class mainWindow(QMainWindow):
    is_port_open_qt = pyqtSignal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.press_stop = False
        self.resize(1450, 800)
        self.__portName = None
        self.setWindowTitle("Aegiverse IMU GUI")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.first_run_flag = True
        #self.imudata_file = cmn.data_manager(fnum=0)
        self.imudata_file_auto = autoSave.atSave_PC_v3(fnum=0)
        self.act.isCali = False  # 地震不用用到校正的功能
        self.menu = self.menuBar()
        self.pig_menu = pig_menu_manager(self.menu, self)
        # -------menu obj------#
        self.pig_parameter_widget = None
        self.pig_cali_menu = calibrationBlock()
        self.pig_initial_setting_menu = myRadioButton.radioButtonBlock_2('SYNC MODE', 'OFF', 'ON', False)  # True
        # means setting 'OFF' state value to True
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['fog', 'wx', 'wy', 'wz'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['wx', 'wy', 'wz', 'ax', 'ay', 'az', 'yy', 'MM', 'dd', 'hh', 'mm', 'ss', 'ms'])
        # -------end of menu obj------#
        self.linkfunction()
        self.act.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()

        self.__debug = debug_en
        self.t_start = time.perf_counter()
        self.autoComPort_v2()  # 直接自動撈取COM Port，且撈取對應的儀器名稱

    def mainUI(self):
        self.setCentralWidget(self.top)

    def linkfunction(self):
        # usb connection
        # self.top.usb.bt_update.clicked.connect(self.updateComPort)
        self.top.usb.bt_update.clicked.connect(self.autoComPort_v2)
        self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
        self.top.usb.bt_connect.clicked.connect(self.connect)
        self.top.usb.bt_disconnect.clicked.connect(self.disconnect)
        # bt connection
        self.top.read_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.stop)
        # rb connection
        #self.top.kal_filter_rb.toggled.connect(lambda: self.update_kalFilter_en(self.top.kal_filter_rb))
        # pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        self.act.buffer_qt.connect(self.printBuffer)
        self.is_port_open_qt.connect(self.is_port_open_status_manager)
        self.act.Portstatus_qt.connect(self.autoDetectComport)
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_parameters,
                                              self.show_calibration_menu,
                                              self.show_plot_data_menu,
                                              self.show_cal_allan_menu,
                                              self.show_initial_setting_menu
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

    def show_initial_setting_menu(self):
        self.pig_initial_setting_menu.show()

    def show_plot_data_menu(self):
        self.analysis_timing_plot.show()

    def show_cal_allan_menu(self):
        self.analysis_allan.show()

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

    def printBuffer_GPS(self):
        self.top.buffer_lb.lb.setText(str(self.act.readInputBuffer()))

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
        if portNum != 0:
            self.top.usb.bt_connect.setEnabled(True) # 判斷是否已連接儀器，並顯示連接btn

    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    # def autoComPort(self):
    #     portNum, portList = self.__connector.portList()
    #     self.__portName = self.top.usb.autoComport(portNum, portList)
    #     if self.__portName["Key1"] != []:
    #         self.top.usb.bt_connect.setEnabled(True) # 判斷是否已連接儀器，並顯示連接btn

    def autoComPort_v2(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.autoComport_v2(portNum, portList)
        if portNum != 0:
            self.top.usb.bt_connect.setEnabled(True) # 判斷是否已連接儀器，並顯示連接btn

    def autoDetectComport(self, status):
        self.top.usb.showPortName_v2(None)
        self.stop()

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        is_port_open = self.act.connect(self.__connector, self.__portName, 230400)
        self.is_port_open_qt.emit(is_port_open)
        #self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
        self.pig_parameter_widget = pig_parameters_widget(self.act, "parameters_SP10.json")
        self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
        self.act.isExtMode = self.pig_initial_setting_menu.btn_status
        # print(self.act.isExtMode)

    def disconnect(self):
        is_port_open = self.act.disconnect()
        self.is_port_open_qt.emit(is_port_open)

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetFPGATimer(self):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1)
        print('main: reset FPGA time')

    def start(self):
        # self.resetFPGATimer()
        self.act.readIMU()
        self.act.isRun = True
        self.press_stop = False
        self.act.start()
        #file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
        # self.imudata_file_.name = file_name
        # self.imudata_file.open(self.top.save_block.rb.isChecked())

        file_name = str(pathlib.Path().absolute())  # 抓取此執行檔案的位置，且不包含此層的檔案名稱
        self.imudata_file_auto.data_path = file_name
        self.imudata_file_auto.start = True
        self.imudata_file_auto.create_data_folder(True)
        self.imudata_file_auto.auto_create_folder(True)
        #
        # if OUTPUT_ONE_AXIS:
        #     self.imudata_file_auto.write_line('time,wx,wy,fog,ax,ay,az,T')
        # else:
        #     self.imudata_file_auto.write_line('time,fog,wx,wy,wz,ax,ay,az,T')

    def stop(self):
        # self.resetFPGATimer()
        self.act.isRun = False
        self.imudata_file_auto.close_hour_folder()
        self.imudata_file_auto.reset_hh_reg()
        self.top.save_block.rb.setChecked(False)
        #self.imudata_file.close()
        self.press_stop = True
        self.first_run_flag = True
        self.act.start_read = 0
        print('press stop')

    @property
    def press_stop(self):
        return self.__stop

    @press_stop.setter
    def press_stop(self, stop):
        self.__stop = stop

    @property
    def first_run_flag(self):
        return self.__first_run_flag

    @first_run_flag.setter
    def first_run_flag(self, flag):
        self.__first_run_flag = flag
        # self.act.first_run_flag = flag

    def collectData(self, imudata):
        if not self.press_stop:
            # print('collectData pre: ', len(imudata['TIME']), end=', ')
            # print(imudata['TIME'])
            #
            # print('collectData after: ', len(imudata['TIME']), end=', ')
            # print(imudata['TIME'])
            # self.first_run_flag = False
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
            debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                         + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
            cmn.print_debug(debug_info, self.__debug)
            # print(imudata["PIG_WZ"])

            # if OUTPUT_ONE_AXIS:
            #     datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
            #         , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
            #     data_fmt = "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f"
            # else:
            #     datalist = [imudata["TIME"], imudata["PIG_WZ"], imudata["NANO33_WX"], imudata["NANO33_WY"],
            #                 imudata["NANO33_WZ"]
            #         , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
            #     data_fmt = "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f"

            datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
                    , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]
                    , imudata["YEAR"], imudata["MON"], imudata["DAY"], imudata["HOUR"]
                    , imudata["MIN"], imudata["SEC"], imudata["mSEC"]]
            data_fmt = "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%d,%d,%d,%d,%d,%d,%d"

            # 撈取PC的時間
            gps_time = '%d/%d/%d %d:%d:%d.%d' % (imudata['YEAR'][0], imudata['MON'][0], imudata['DAY'][0],
                                                 imudata['HOUR'][0], imudata['MIN'][0], imudata['SEC'][0],
                                                 imudata['mSEC'][0])

            self.printGPS_Time(gps_time)
            self.imudata_file_auto.saveData(datalist, data_fmt)
            self.imudata_file_auto.judgment_hh(True)
            self.plotdata_v2(self.imudata)
            self.printUpdateRate(self.imudata["TIME"])
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

    def plotdata_v2(self, imudata):
        # print('plotdata: ', imudata['TIME'])
        # if self.top.plot1_unit_rb.btn_status == 'dph':
        #     factor = 3600
        # else:
        #     factor = 1
        #self.top.plot1.ax.setData(imudata["TIME"], imudata["NANO33_WZ"] * factor)  # 為mems的值

        # 20230608 修改
        self.top.plot1.ax.setData(imudata["TIME"], imudata["NANO33_WZ"])
        self.top.plot2.ax.setData(imudata["TIME"], imudata["ADXL_AX"])
        self.top.plot3.ax.setData(imudata["TIME"], imudata["ADXL_AY"])
        self.top.plot4.ax.setData(imudata["TIME"], imudata["ADXL_AZ"])
        self.top.plot5.ax.setData(imudata["TIME"], imudata["NANO33_WX"])
        self.top.plot6.ax.setData(imudata["TIME"], imudata["NANO33_WY"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
