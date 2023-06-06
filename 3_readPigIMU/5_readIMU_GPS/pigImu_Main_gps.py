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
from datetime import datetime
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
from pigImu_Widget_gps import pigImuWidget as TOP
from pigImuReader_gps import pigImuReader as ACTION
from pigImuReader import pigImuReader as ACTION_PIG
from pigImuReader_gps import IMU_DATA_STRUCTURE
from pigImuReader import IMU_DATA_STRUCTURE as PIG_DATA_STRUCTURE
import numpy as np


class mainWindow(QMainWindow):
    is_port_open_qt = pyqtSignal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()

        self.update_rate = None
        self.press_stop = False
        self.resize(1450, 800)
        self.pig_parameter_widget = None
        self.pig_parameter_widget_sp9 = None
        self.__portName = None
        self.__skipcnt = 0
        self.__skiptime = 0
        self.setWindowTitle("AegiverseIMU")
        self.__connector = Connector()
        self.__connector_sp9 = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.act_sp9 = ACTION_PIG()
        # self.imudata_file = cmn.data_manager(fnum=0)
        self.imudata_file_auto = autoSave.atSave_PC(fnum=0)
        self.pig_cali_menu = calibrationBlock()
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['fog'])
        # self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
        #     ['fog', 'ax', 'ay', 'az', 'T', 'yy', 'MM', 'dd', 'hh', 'mm', 'ss'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['fog', 'T', 'yy', 'MM', 'dd', 'hh', 'mm', 'ss'])
        self.act.isCali = True
        self.act_sp9.isCali = True
        self.menu = self.menuBar()
        self.pig_menu = pig_menu_manager(self.menu, self)
        self.linkfunction()
        self.act.arrayNum = 10
        self.act_sp9.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()
        self.sp9_data = self.resetDataContainer_sp9()
        self.imudata_sp9 = self.resetDataContainer_sp9()

        self.__debug = debug_en
        self.t_start = time.perf_counter()

    def mainUI(self):
        self.setCentralWidget(self.top)

    def linkfunction(self):
        # usb connection
        self.top.usb.bt_update.clicked.connect(self.autoComport)
        # self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
        self.top.usb.bt_connect.clicked.connect(self.connect)
        self.top.usb.bt_disconnect.clicked.connect(self.disconnect)
        # bt connection
        self.top.read_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.stop)
        # rb connection
        self.top.kal_filter_rb.toggled.connect(lambda: self.update_kalFilter_en(self.top.kal_filter_rb))
        # pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act_sp9.imudata_qt.connect(self.collectData_sp9)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        self.act_sp9.imuThreadStop_qt.connect(self.imuThreadStopDetect_sp9)
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
        self.update_rate = round(((t_list[-1] - t_list[0]) / (len(t_list) - 1)) ** -1, 1)
        self.top.data_rate_lb.lb.setText(str(self.update_rate))
        self.act.dataRate = self.update_rate

    # def updateComPort(self):
    #     portNum, portList = self.__connector.portList()
    #     self.top.usb.addPortItems(portNum, portList)
        # print(portList)

    def autoComport(self):
        portNum, portList = self.__connector.portList()

        self.__portName = self.top.usb.autoComport(portNum, portList)

    # def selectComPort(self):
    #     self.__portName = self.top.usb.selectPort()
    #     logger.debug('selectComPort.__portName: %s' % self.__portName)

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        print(self.__portName)
        is_port_open = self.act.connect(self.__connector, self.__portName['SP10'], 230400)
        self.act_sp9.connect(self.__connector_sp9, self.__portName['SP9'], 230400)
        self.is_port_open_qt.emit(is_port_open)
        self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
        self.pig_parameter_widget_sp9 = pig_parameters_widget(self.act_sp9, 'parameters_SP9' + '.json')
        self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
        self.act_sp9.isCali_w = True

    def disconnect(self):
        is_port_open = self.act.disconnect()
        self.act_sp9.disconnect()
        self.is_port_open_qt.emit(is_port_open)

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def imuThreadStopDetect_sp9(self):
        self.imudata_sp9 = self.resetDataContainer_sp9()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetDataContainer_sp9(self):
        return {k: np.empty(0) for k in set(PIG_DATA_STRUCTURE)}

    def resetFPGATimer(self):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1)
        self.act_sp9.writeImuCmd(CMD_FOG_TIMER_RST, 1)

    def start(self):
        self.resetFPGATimer()
        self.act.readIMU()
        self.act_sp9.readIMU()
        self.act.isRun = True
        self.act_sp9.isRun = True
        self.press_stop = False
        self.act.start()
        self.act_sp9.start()
        self.__skipcnt = 0
        file_name = self.top.save_block.le_filename.text()
        # self.imudata_file.name = file_name
        # self.imudata_file.open(self.top.save_block.rb.isChecked())
        # self.imudata_file.write_line('time,fog,ax,ay,az,T,yy,MM,dd,hh,mm,ss')

        self.imudata_file_auto.data_path = file_name
        self.imudata_file_auto.start = True
        self.imudata_file_auto.create_data_folder(self.top.save_block.rb.isChecked())
        self.imudata_file_auto.auto_create_folder(self.top.save_block.rb.isChecked())
        self.imudata_file_auto.write_line('time,wx,wy,wz,ax,ay,az,yy,MM,dd,hh,mm,ss')

    def stop(self):
        self.resetFPGATimer()
        self.act.isRun = False
        self.act_sp9.isRun = False
        self.top.save_block.rb.setChecked(False)
        # self.imudata_file.close()
        self.imudata_file_auto.close_hour_folder()
        self.press_stop = True

    @property
    def press_stop(self):
        return self.__stop

    @press_stop.setter
    def press_stop(self, stop):
        self.__stop = stop

    def collectData_sp9(self, imudata):
        if not self.press_stop:
            self.sp9_data = imudata

    def collectData(self, imudata):
        # print(len(imudata["TIME"]))
        sample = 1000
        if not self.press_stop:
            # print(imudata)

            input_buf = self.act.readInputBuffer()
            t0 = time.perf_counter()
            self.printPdTemperature(imudata["PD_TEMP"][0])
            t1 = time.perf_counter()
            # start of sp9 data
            if len(self.sp9_data["TIME"]) == 0: # wait sp9 data coming
                return
            self.imudata_sp9["TIME"] = np.append(self.imudata_sp9["TIME"], self.sp9_data["TIME"])
            self.imudata_sp9["PIG_WZ"] = np.append(self.imudata_sp9["PIG_WZ"], self.sp9_data["PIG_WZ"])
            self.imudata_sp9["PD_TEMP"] = np.append(self.imudata_sp9["PD_TEMP"], self.sp9_data["PD_TEMP"])
            self.imudata_sp9["PIG_ERR"] = np.append(self.imudata_sp9["PIG_ERR"], self.sp9_data["PIG_ERR"])
            # end of sp9 data
            self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"])
            self.imudata["PIG_WZ"] = np.append(self.imudata["PIG_WZ"], imudata["PIG_WZ"])
            self.imudata["PD_TEMP"] = np.append(self.imudata["PD_TEMP"], imudata["PD_TEMP"])
            self.imudata["ADXL_AX"] = np.append(self.imudata["ADXL_AX"], imudata["ADXL_AX"])
            self.imudata["ADXL_AY"] = np.append(self.imudata["ADXL_AY"], imudata["ADXL_AY"])
            self.imudata["ADXL_AZ"] = np.append(self.imudata["ADXL_AZ"], imudata["ADXL_AZ"])
            self.imudata["NANO33_WX"] = np.append(self.imudata["NANO33_WX"], imudata["NANO33_WX"])
            self.imudata["NANO33_WY"] = np.append(self.imudata["NANO33_WY"], imudata["NANO33_WY"])
            self.imudata["NANO33_WZ"] = np.append(self.imudata["NANO33_WZ"], imudata["NANO33_WZ"])
            if len(self.imudata["TIME"]) > sample:
                self.imudata_sp9["TIME"] = self.imudata_sp9["TIME"][
                                           self.act_sp9.arrayNum:self.act_sp9.arrayNum + sample]
                self.imudata_sp9["PIG_WZ"] = self.imudata_sp9["PIG_WZ"][
                                             self.act_sp9.arrayNum:self.act_sp9.arrayNum + sample]
                self.imudata_sp9["PIG_ERR"] = self.imudata_sp9["PIG_ERR"][
                                              self.act_sp9.arrayNum:self.act_sp9.arrayNum + sample]
                self.imudata_sp9["PD_TEMP"] = self.imudata_sp9["PD_TEMP"][
                                              self.act_sp9.arrayNum:self.act_sp9.arrayNum + sample]
                self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["PIG_WZ"] = self.imudata["PIG_WZ"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["PD_TEMP"] = self.imudata["PD_TEMP"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["ADXL_AX"] = self.imudata["ADXL_AX"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["ADXL_AY"] = self.imudata["ADXL_AY"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["ADXL_AZ"] = self.imudata["ADXL_AZ"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["NANO33_WX"] = self.imudata["NANO33_WX"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["NANO33_WY"] = self.imudata["NANO33_WY"][self.act.arrayNum:self.act.arrayNum + sample]
                self.imudata["NANO33_WZ"] = self.imudata["NANO33_WZ"][self.act.arrayNum:self.act.arrayNum + sample]
            t2 = time.perf_counter()
            self.printUpdateRate(self.imudata["TIME"])
            # print('sp9: ', len(self.imudata_sp9["PD_TEMP"]), self.sp9_data["TIME"])
            # print('sp10: ', len(self.imudata["PD_TEMP"]), imudata['TIME'])
            if self.__skipcnt < 10:
                self.__skipcnt += 1
                # print('self.__skipcnt: ', self.__skipcnt)
                return

            debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                         + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
            cmn.print_debug(debug_info, self.__debug)

            datalist = [imudata["TIME"], imudata["PIG_WZ"], self.sp9_data["PIG_WZ"], self.sp9_data["PIG_WZ"]
                , imudata['GPS_YEAR'], imudata['GPS_MON'], imudata['GPS_DAY'], imudata['GPS_HOUR']
                , imudata['GPS_MIN'], imudata['GPS_SEC']
                        ]
            data_fmt = "%.4f,%.5f,%.5f,%.5f,%d,%d,%d,%d,%d,%.2f"
            gps_time = '%d/%d/%d %d:%d:%.1f' % (imudata['GPS_YEAR'][0], imudata['GPS_MON'][0], imudata['GPS_DAY'][0],
                                                imudata['GPS_HOUR'][0], imudata['GPS_MIN'][0], imudata['GPS_SEC'][0])
            self.printGPS_Time(gps_time)
            self.imudata_file_auto.saveData(datalist, data_fmt)
            self.imudata_file_auto.auto_create_folder(self.top.save_block.rb.isChecked())
            self.plotdata(self.imudata, self.imudata_sp9["PIG_WZ"])

    def plotdata(self, imudata, pig_sp9):

        if self.top.plot1_unit_rb.btn_status == 'dph':
            factor = 3600
        else:
            factor = 1

        if self.top.plot1_showWz_cb.cb_1.isChecked():
            self.top.plot1.ax1.setData(imudata["TIME"], imudata["PIG_WZ"] * factor)
        else:
            self.top.plot1.ax1.clear()
        if self.top.plot1_showWz_cb.cb_2.isChecked():
            self.top.plot1.ax2.setData(imudata["TIME"], pig_sp9 * factor)
        else:
            self.top.plot1.ax2.clear()

        self.top.plot2.ax.setData(imudata["ADXL_AX"])
        # self.top.plot2.title = 'NANO33_AX'
        self.top.plot3.ax.setData(imudata["ADXL_AY"])
        self.top.plot4.ax.setData(imudata["ADXL_AZ"])
        # self.top.plot5.ax.setData(imudata["NANO33_WX"])
        # self.top.plot6.ax.setData(imudata["NANO33_WY"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
