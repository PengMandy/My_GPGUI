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
from myLib.myGui import analysis_Allan, analysis_TimingPlot, myRadioButton
from myLib.myGui import autoSave
from PyQt5.QtWidgets import *
from pigImu_Widget_gps_2 import pigImuWidget as TOP
from pigImuReader_gps import pigImuReader as ACTION
from pigImuReader import pigImuReader as ACTION_PIG
from pigImuReader_gps import IMU_DATA_STRUCTURE
from pigImuReader import IMU_DATA_STRUCTURE as PIG_DATA_STRUCTURE
import numpy as np


class mainWindow(QMainWindow):
    is_port_open_qt = pyqtSignal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()

        # self.update_rate = None
        self.press_stop = False
        self.resize(1450, 800)
        self.pig_parameter_widget = None
        self.pig_parameter_widget_sp11 = None
        self.pig_parameter_widget_sp13 = None
        self.__portName = None
        self.__skipcnt = 0
        self.__skiptime = 0
        self.setWindowTitle("AegiverseIMU")
        # 20230531 這邊直接建三個connector的類別物件
        self.__connector = Connector()
        self.__connector_sp11 = Connector()
        self.__connector_sp13 = Connector()
        self.__isFileOpen = False
        self.menu = self.menuBar()
        self.top = TOP(self.menu)
        # 20230531 直接建三個Reader的類別物件
        self.act = ACTION()
        self.act_sp11 = ACTION_PIG()
        self.act_sp13 = ACTION_PIG()
        # self.imudata_file = cmn.data_manager(fnum=0)
        self.imudata_file_auto = autoSave.atSave_PC_v2(fnum=0)   # 自動儲存檔案的類別
        self.pig_cali_menu = calibrationBlock()
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['fog'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['wx', 'wy', 'wz', 'ax', 'ay', 'az', 'yy', 'MM', 'dd', 'hh', 'mm', 'ss', 'ms'])
        # 20230531 直接用三個判斷calibration的變數
        self.act.isCali = True
        self.act_sp11.isCali = True
        self.act_sp13.isCali = True

        #self.pig_menu = pig_menu_manager(self.menu, self)
        self.pig_initail_setting_menu = myRadioButton.radioButtonBlock_2('SYNC MODE', 'OFF', 'ON', False)  # True
        self.linkfunction()
        self.act.arrayNum = 10
        self.act_sp11.arrayNum = 10
        self.act_sp13.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()
        self.sp11_data = self.resetDataContainer_sp11()
        self.imudata_sp11 = self.resetDataContainer_sp11()
        self.sp13_data = self.resetDataContainer_sp13()
        self.imudata_sp13 = self.resetDataContainer_sp13()

        self.__debug = debug_en
        self.t_start = time.perf_counter()
        self.act.date_type = self.top.date_rb.btn_status
        self.autoComport()

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
        # self.top.kal_filter_rb.toggled.connect(lambda: self.update_kalFilter_en(self.top.kal_filter_rb))
        # pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act_sp11.imudata_qt.connect(self.collectData_sp11)
        self.act_sp13.imudata_qt.connect(self.collectData_sp13)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        self.act_sp11.imuThreadStop_qt.connect(self.imuThreadStopDetect_sp11)
        self.act_sp13.imuThreadStop_qt.connect(self.imuThreadStopDetect_sp13)
        # self.act.buffer_qt.connect(self.printBuffer)
        self.is_port_open_qt.connect(self.is_port_open_status_manager)
        # menu trigger connection
        self.top.pig_menu.action_trigger_connect([self.show_parameters,
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
        self.pig_initail_setting_menu.show()

    def show_plot_data_menu(self):
        self.analysis_timing_plot.show()

    def show_cal_allan_menu(self):
        self.analysis_allan.show()

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self):
        # self.top.buffer_lb.lb.setText(str(val))
        self.top.buffer_lb.lb.setText(str(self.act.readInputBuffer()))
        self.top.buffer_lb_2.lb.setText(str(self.act.readInputBuffer()))
        self.top.buffer_lb_3.lb.setText(str(self.act.readInputBuffer()))

    def printGPS_Time(self, val):
        self.top.gpstime_lb.lb.setText(val)

    def printPdTemperature(self, val, val2, val3):
        if (time.perf_counter() - self.t_start) > 0.5:
            self.top.pd_temp_lb.lb.setText(str(val))
            self.top.pd_temp_lb_2.lb.setText(str(val2))
            self.top.pd_temp_lb_3.lb.setText(str(val3))
            self.t_start = time.perf_counter()

    def printUpdateRate(self, t_list, t_list_2, t_list_3):
        update_rate = round(((t_list[-1] - t_list[0]) / (len(t_list) - 1)) ** -1, 1)
        update_rate_2 = round(((t_list_2[-1] - t_list_2[0]) / (len(t_list_2) - 1)) ** -1, 1)
        update_rate_3 = round(((t_list_3[-1] - t_list_3[0]) / (len(t_list_3) - 1)) ** -1, 1)
        self.top.data_rate_lb.lb.setText(str(update_rate))
        self.top.data_rate_lb_2.lb.setText(str(update_rate_2))
        self.top.data_rate_lb_3.lb.setText(str(update_rate_3))
        self.act.dataRate = update_rate

    def autoComport(self):
        portNum, portList = self.__connector.portList()

        self.__portName = self.top.usb.autoComport(portNum, portList)

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.top.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        print(self.__portName)
        is_port_open = self.act.connect(self.__connector, self.__portName['SP10'], 230400)
        self.act_sp11.connect(self.__connector_sp11, self.__portName['SP11'], 230400)
        self.act_sp13.connect(self.__connector_sp13, self.__portName['SP13'], 230400)
        self.is_port_open_qt.emit(is_port_open)
        # self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
        self.pig_parameter_widget = pig_parameters_widget(self.act, 'parameters_SP10' + '.json')
        self.pig_parameter_widget_sp11 = pig_parameters_widget(self.act_sp11, 'parameters_SP11' + '.json')
        self.pig_parameter_widget_sp13 = pig_parameters_widget(self.act_sp13, 'parameters_SP13' + '.json')
        self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
        self.act_sp11.isCali_w = True
        self.act_sp13.isCali_w = True

    def disconnect(self):
        is_port_open = self.act.disconnect()
        self.act_sp11.disconnect()
        self.act_sp13.disconnect()
        self.is_port_open_qt.emit(is_port_open)

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def imuThreadStopDetect_sp11(self):
        self.imudata_sp11 = self.resetDataContainer_sp11()

    def imuThreadStopDetect_sp13(self):
        self.imudata_sp13 = self.resetDataContainer_sp13()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetDataContainer_sp11(self):
        return {k: np.empty(0) for k in set(PIG_DATA_STRUCTURE)}

    def resetDataContainer_sp13(self):
        return {k: np.empty(0) for k in set(PIG_DATA_STRUCTURE)}

    def resetFPGATimer(self):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1)
        self.act_sp11.writeImuCmd(CMD_FOG_TIMER_RST, 1)
        self.act_sp13.writeImuCmd(CMD_FOG_TIMER_RST, 1)

    def start(self):
        self.resetFPGATimer()
        self.act.readIMU()
        self.act_sp11.readIMU()
        self.act_sp13.readIMU()
        self.act.isRun = True
        self.act_sp11.isRun = True
        self.act_sp13.isRun = True
        self.press_stop = False
        self.act.start()
        self.act_sp11.start()
        self.act_sp13.start()
        self.__skipcnt = 0
        file_name = self.top.save_block.le_filename.text()
        # self.imudata_file.name = file_name
        # self.imudata_file.open(self.top.save_block.rb.isChecked())
        # self.imudata_file.write_line('time,fog,ax,ay,az,T,yy,MM,dd,hh,mm,ss')

        self.imudata_file_auto.data_path = file_name
        self.imudata_file_auto.start = True
        self.imudata_file_auto.create_data_folder(self.top.save_block.rb.isChecked())
        self.imudata_file_auto.auto_create_folder(self.top.save_block.rb.isChecked())
        # self.imudata_file_auto.write_line('time,wx,wy,wz,ax,ay,az,yy,MM,dd,hh,mm,ss')

    def stop(self):
        self.resetFPGATimer()
        self.act.isRun = False
        self.act_sp11.isRun = False
        self.act_sp13.isRun = False
        if self.top.save_block.rb.isChecked():
            self.imudata_file_auto.close_hour_folder()
            self.imudata_file_auto.reset_hh_reg()
            self.top.save_block.rb.setChecked(False)
        self.press_stop = True

    @property
    def press_stop(self):
        return self.__stop

    @press_stop.setter
    def press_stop(self, stop):
        self.__stop = stop

    def collectData_sp11(self, imudata):
        if not self.press_stop:
            self.sp11_data = imudata

    def collectData_sp13(self, imudata):
        if not self.press_stop:
            self.sp13_data = imudata

    def collectData(self, imudata):
        # print(len(imudata["TIME"]))
        sample = 1000
        if not self.press_stop:
            # print(imudata)
            self.act.date_type = self.top.date_rb.btn_status
            self.printBuffer()
            input_buf = self.act.readInputBuffer()
            t0 = time.perf_counter()

            t1 = time.perf_counter()
            # start of sp11 data
            if len(self.sp11_data["TIME"]) == 0 or len(self.sp13_data["TIME"]) == 0 or len(
                    imudata['TIME']) == 0:  # wait sp11 data coming
                # print(len(imudata["TIME"]), len(self.sp11_data["TIME"]), len(self.sp11_data["TIME"]))
                # print('wait!!!!!!!!!!!!!!!!')
                return

            self.imudata_sp11["TIME"] = np.append(self.imudata_sp11["TIME"], self.sp11_data["TIME"])
            self.imudata_sp11["PIG_WZ"] = np.append(self.imudata_sp11["PIG_WZ"], self.sp11_data["PIG_WZ"])
            self.imudata_sp11["PD_TEMP"] = np.append(self.imudata_sp11["PD_TEMP"], self.sp11_data["PD_TEMP"])
            self.imudata_sp11["PIG_ERR"] = np.append(self.imudata_sp11["PIG_ERR"], self.sp11_data["PIG_ERR"])
            # end of sp11 data
            # start of sp13 data
            self.imudata_sp13["TIME"] = np.append(self.imudata_sp13["TIME"], self.sp13_data["TIME"])
            self.imudata_sp13["PIG_WZ"] = np.append(self.imudata_sp13["PIG_WZ"], self.sp13_data["PIG_WZ"])
            self.imudata_sp13["PD_TEMP"] = np.append(self.imudata_sp13["PD_TEMP"], self.sp13_data["PD_TEMP"])
            self.imudata_sp13["PIG_ERR"] = np.append(self.imudata_sp13["PIG_ERR"], self.sp13_data["PIG_ERR"])
            # end of sp13 data
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
                self.imudata_sp11["TIME"] = self.imudata_sp11["TIME"][
                                            self.act_sp11.arrayNum:self.act_sp11.arrayNum + sample]
                self.imudata_sp11["PIG_WZ"] = self.imudata_sp11["PIG_WZ"][
                                              self.act_sp11.arrayNum:self.act_sp11.arrayNum + sample]
                self.imudata_sp11["PIG_ERR"] = self.imudata_sp11["PIG_ERR"][
                                               self.act_sp11.arrayNum:self.act_sp11.arrayNum + sample]
                self.imudata_sp11["PD_TEMP"] = self.imudata_sp11["PD_TEMP"][
                                               self.act_sp11.arrayNum:self.act_sp11.arrayNum + sample]
                self.imudata_sp13["TIME"] = self.imudata_sp13["TIME"][
                                            self.act_sp13.arrayNum:self.act_sp13.arrayNum + sample]
                self.imudata_sp13["PIG_WZ"] = self.imudata_sp13["PIG_WZ"][
                                              self.act_sp13.arrayNum:self.act_sp13.arrayNum + sample]
                self.imudata_sp13["PIG_ERR"] = self.imudata_sp13["PIG_ERR"][
                                               self.act_sp13.arrayNum:self.act_sp13.arrayNum + sample]
                self.imudata_sp13["PD_TEMP"] = self.imudata_sp13["PD_TEMP"][
                                               self.act_sp13.arrayNum:self.act_sp13.arrayNum + sample]
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

            if self.__skipcnt < 10:
                self.__skipcnt += 1
                # print('self.__skipcnt: ', self.__skipcnt)
                return
            # self.printUpdateRate(self.imudata["TIME"], self.imudata_sp11["TIME"], self.imudata_sp13["TIME"])
            self.printUpdateRate(imudata["TIME"], self.sp11_data["TIME"], self.sp13_data["TIME"])
            self.printPdTemperature(imudata["PD_TEMP"][0], self.sp11_data["PD_TEMP"][0], self.sp13_data["PD_TEMP"][0])
            debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                         + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
            cmn.print_debug(debug_info, self.__debug)
            # print(self.top.date_rb.btn_status)


            # datalist = [imudata["TIME"], imudata["PIG_WZ"], self.sp11_data["PIG_WZ"], self.sp13_data["PIG_WZ"]
            #             , imudata['YEAR'], imudata['MON'], imudata['DAY'], imudata['HOUR']
            #             , imudata['MIN'], imudata['SEC']]
            datalist = [imudata["TIME"], self.sp13_data["PIG_WZ"], self.sp11_data["PIG_WZ"], imudata["PIG_WZ"]
                , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]
                , imudata['YEAR'], imudata['MON'], imudata['DAY'], imudata['HOUR']
                , imudata['MIN'], imudata['SEC'], imudata['mSEC']]
            # print('main:', imudata['YEAR'], imudata['MON'], imudata['DAY'], imudata['HOUR'], imudata['MIN'],
            #       imudata['SEC'])
            # data_fmt = "%.4f,%.5f,%.5f,%.5f,%d,%d,%d,%d,%d,%.2f"
            data_fmt = "%.4f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%d,%d,%d,%d,%d,%d,%d"
            gps_time = '%d/%d/%d %d:%d:%d.%d' % (imudata['YEAR'][0], imudata['MON'][0], imudata['DAY'][0],
                                                 imudata['HOUR'][0], imudata['MIN'][0], imudata['SEC'][0],
                                                 imudata['mSEC'][0])
            self.printGPS_Time(gps_time)
            self.imudata_file_auto.saveData(datalist, data_fmt)
            self.imudata_file_auto.auto_create_folder(self.top.save_block.rb.isChecked())
            self.plotdata(self.imudata, self.imudata_sp11["PIG_WZ"], self.imudata_sp13["PIG_WZ"])

    def plotdata(self, imudata, pig_sp11, pig_sp13):
        # self.plotControl()
        self.top.plot1.ax.setData(imudata["TIME"], pig_sp13)
        self.top.plot2.ax.setData(imudata["TIME"], pig_sp11)
        self.top.plot3.ax.setData(imudata["TIME"], imudata["PIG_WZ"])
        self.top.plot4.ax.setData(imudata["TIME"], imudata["ADXL_AX"])
        self.top.plot5.ax.setData(imudata["TIME"], imudata["ADXL_AY"])
        self.top.plot6.ax.setData(imudata["TIME"], imudata["ADXL_AZ"])

    def plotControl(self):
        self.top.plot1.p.setLimits(minYRange=0.4)
        self.top.plot2.p.setLimits(minYRange=0.4)
        self.top.plot3.p.setLimits(minYRange=0.4)
        self.top.plot4.p.setLimits(minYRange=0.4)
        self.top.plot5.p.setLimits(minYRange=0.4)
        self.top.plot6.p.setLimits(minYRange=0.4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
