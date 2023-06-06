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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from myLib import common as cmn

PRINT_DEBUG = 0


class usbConnect():
    def __init__(self, group_name='Connect COM port'):

        self.__portList = None
        self.__groupBox = QGroupBox(group_name)
        self.__groupBox.setFont(QFont('Arial', 10))
        # self.__groupBox.setCheckable(True)
        self.bt_update = QPushButton("update")
        self.bt_connect = QPushButton('connect')
        self.bt_connect.setEnabled(False)  # 20230606 判斷是否update儀器
        self.bt_disconnect = QPushButton('disconnect')
        self.bt_disconnect.setEnabled(False)
        self.cb = QComboBox()
        self.lb_status = QLabel(" ")
        self.lb_comDisp = QLabel(" ")

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.bt_update, 0, 0, 1, 1)
        layout.addWidget(self.cb, 0, 1, 1, 1)
        layout.addWidget(self.bt_connect, 0, 2, 1, 1)
        layout.addWidget(self.bt_disconnect, 0, 3, 1, 1)
        layout.addWidget(self.lb_comDisp, 1, 0, 1, 2)
        layout.addWidget(self.lb_status, 1, 2, 1, 2)
        self.__groupBox.setLayout(layout)
        return self.__groupBox

    def addPortItems(self, num, ports):
        self.__portList = ports
        self.cb.clear()
        logger.debug('port_num: %d' % num)
        # logger.debug('ports: %s' % ports[0])
        # logger.debug(dir(ports[0]))
        # logger.debug('ports.description: %s' % ports[0].description)
        # logger.debug('ports.device: %s' % ports[0].device)
        # logger.debug('ports.name: %s' % ports[0].name)
        if num > 0:
            for i in range(num):
                self.cb.addItem(ports[i].device)
                logger.debug('port_name: %s' % ports[i].device)
                logger.debug('ports.description: %s' % ports[i].description)
                logger.debug('ports.hwid: %s' % ports[i].hwid)
                logger.debug('ports.serial_number: %s' % ports[i].serial_number)
                logger.debug('ports.product: %s' % ports[i].product)
                logger.debug('ports.manufacturer: %s' % ports[i].manufacturer)
                logger.debug('ports.location: %s\n' % ports[i].location)

    def selectPort(self):
        idx = self.cb.currentIndex()
        self.lb_comDisp.setText(self.__portList[idx].description)
        return self.__portList[idx].device

    def updateStatusLabel(self, is_open):
        self.bt_connect.setEnabled(not is_open)
        self.bt_disconnect.setEnabled(is_open)

        if is_open:
            self.SetConnectText(Qt.blue, "is connected")
            # self.lb_status.setText("is connected")
        else:
            self.SetConnectText(Qt.red, "is disconnected")
            # self.lb_status.setText("is disconnected")

    def show(self):
        QB = self.layout()
        QB.show()

    def SetConnectText(self, color, text):
        pe = QPalette()
        pe.setColor(QPalette.WindowText, color)
        self.lb_status.setPalette(pe)
        self.lb_status.setFont(QFont("Arial", 12))
        self.lb_status.setText(text)
        # self.lb_status.setAlignment(Qt.AlignCenter)
        # self.lb_comDisp.show()


class usbConnect_auto():
    def __init__(self, group_name='Connect COM port', key1='SP10', key2='SP11', key3='SP13'):

        self.__portList = None
        self.__groupBox = QGroupBox(group_name)
        self.__groupBox.setFont(QFont('Arial', 10))
        self.__key1 = key1
        self.__key2 = key2
        self.__key3 = key3
        self.__port = {key1: '', key2: '', key3: ''}
        # self.__groupBox.setCheckable(True)
        self.bt_update = QPushButton("update")
        self.bt_connect = QPushButton('connect')
        self.bt_disconnect = QPushButton('disconnect')
        self.bt_disconnect.setEnabled(False)
        # self.cb = QComboBox()
        self.lb_status = QLabel(" ")
        self.lb_comDisp = QLabel(" ")

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.bt_update, 0, 0, 1, 1)
        # layout.addWidget(self.cb, 0, 1, 1, 1)
        layout.addWidget(self.bt_connect, 0, 1, 1, 1)
        layout.addWidget(self.bt_disconnect, 0, 2, 1, 1)
        layout.addWidget(self.lb_comDisp, 1, 0, 1, 2)
        layout.addWidget(self.lb_status, 1, 2, 1, 2)
        self.__groupBox.setLayout(layout)
        return self.__groupBox

    def autoComport(self, num, ports):
        self.__portList = ports
        # self.cb.clear()
        logger.debug('port_num: %d' % num)
        # port = dict()
        if num > 0:
            for i in range(num):
                # print(ports[i].serial_number)
                # if ports[i].serial_number == 'AQ6YNJG3A':  # SP9
                #     self.__port[self.__key1] = ports[i].device
                if ports[i].serial_number == 'AG0K5XWMA':  # SP10
                    self.__port[self.__key1] = ports[i].device
                elif ports[i].serial_number == 'AQ00D86ZA':  # SP11
                    self.__port[self.__key2] = ports[i].device
                elif ports[i].serial_number == 'AQ00DQ0HA':  # SP13
                    self.__port[self.__key3] = ports[i].device
        logger.debug('autoComport: %s\n' % self.__port)
        self.showPortName(self.__port)
        return self.__port

    def showPortName(self, port):
        # idx = self.cb.currentIndex()
        self.lb_comDisp.setText(self.__key1 + ':' + port[self.__key1] + ', ' + self.__key2 + ':' + port[self.__key2] +
                                ', ' + self.__key3 + ':' + port[self.__key3])
        # return self.__portList[idx].device

    def updateStatusLabel(self, is_open):
        self.bt_connect.setEnabled(not is_open)
        self.bt_disconnect.setEnabled(is_open)

        if is_open:
            self.SetConnectText(Qt.blue, "is connected")
            # self.lb_status.setText("is connected")
        else:
            self.SetConnectText(Qt.red, "is disconnected")
            # self.lb_status.setText("is disconnected")

    def show(self):
        QB = self.layout()
        QB.show()

    def SetConnectText(self, color, text):
        pe = QPalette()
        pe.setColor(QPalette.WindowText, color)
        self.lb_status.setPalette(pe)
        self.lb_status.setFont(QFont("Arial", 12))
        self.lb_status.setText(text)
        # self.lb_status.setAlignment(Qt.AlignCenter)
        # self.lb_comDisp.show()


# class dataSaveBlock(QGroupBox):
#     def __init__(self, name=""):
#         super(dataSaveBlock, self).__init__()
#         self.setTitle(name)
#         self.rb = QRadioButton("save")
#         self.le_filename = QLineEdit("enter_file_name")
#         self.le_ext = QLineEdit(".txt")
#         self.rb.setChecked(False)
#
#         layout = QGridLayout()
#         layout.addWidget(self.rb, 0, 0, 1, 1)
#         layout.addWidget(self.le_filename, 0, 1, 1, 3)
#         layout.addWidget(self.le_ext, 0, 4, 1, 1)
#         self.setLayout(layout)
#
#
# class lineEditBlock(QGroupBox):
#     def __init__(self, name=""):
#         super(lineEditBlock, self).__init__()
#         self.setTitle(name)
#         self.le_filename = QLineEdit("parameters_SP9")
#
#         layout = QGridLayout()
#         layout.addWidget(self.le_filename, 0, 1, 1, 1)
#         self.setLayout(layout)


class spinBlock(QGroupBox):
    def __init__(self, title, minValue, maxValue, step=1, double=False, Decimals=2):
        super(spinBlock, self).__init__()
        if double:
            self.spin = QDoubleSpinBox()
            self.spin.setDecimals(Decimals)
        else:
            self.spin = QSpinBox()

        self.spin.setRange(minValue, maxValue)
        self.spin.setSingleStep(step)
        self.setTitle(title)

        layout = QHBoxLayout()
        layout.addWidget(self.spin)
        self.setLayout(layout)


class spinBlockOneLabel(QGroupBox):
    def __init__(self, title, minValue, maxValue, double=False, step=1, Decimals=2):
        super(spinBlockOneLabel, self).__init__()
        if double:
            self.spin = QDoubleSpinBox()
            self.spin.setDecimals(Decimals)
        else:
            self.spin = QSpinBox()

        self.spin.setRange(minValue, maxValue)
        self.spin.setSingleStep(step)
        self.lb = QLabel('freq')
        self.setTitle(title)

        layout = QHBoxLayout()
        layout.addWidget(self.spin)
        layout.addWidget(self.lb)
        self.setLayout(layout)


class sliderBlock(QGroupBox):
    def __init__(self, title, minValue, maxValue, curValue, step=1, interval=100, parent=None):
        super(sliderBlock, self).__init__(parent)
        self.setTitle(title)
        self.sd = QSlider(Qt.Horizontal)
        self.sd.setMinimum(minValue)
        self.sd.setMaximum(maxValue)
        self.sd.setValue(curValue)
        self.sd.setSingleStep(step)
        self.sd.setTickInterval(interval)
        self.sd.setTickPosition(QSlider.TicksBelow)
        layout = QVBoxLayout()
        layout.addWidget(self.sd)
        self.setLayout(layout)


class editBlock(QGroupBox):
    def __init__(self, title, parent=None):
        super(editBlock, self).__init__(parent)
        self.le = QLineEdit()
        self.setTitle(title)

        layout = QHBoxLayout()
        layout.addWidget(self.le)
        self.setLayout(layout)


# class displayOneBlock(QGroupBox):
#     def __init__(self, name='name'):
#         super(displayOneBlock, self).__init__()
#         self.setTitle(name)
#         self.setFont(QFont('', 10))
#         pe = QPalette()
#         pe.setColor(QPalette.WindowText, Qt.yellow)
#         pe.setColor(QPalette.Window, Qt.black)
#         self.lb = QLabel()
#         self.lb.setPalette(pe)
#         self.lb.setFont(QFont('Arial', 20))
#         self.lb.setAutoFillBackground(True)
#         self.lb.setText('buffer')
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.lb)
#         self.setLayout(layout)


# class checkBoxBlock_2(QGroupBox):
#     def __init__(self, title='', name1='', name2=''):
#         super(checkBoxBlock_2, self).__init__()
#         self.setTitle(title)
#         self.cb_1 = QCheckBox(name1)
#         self.cb_2 = QCheckBox(name2)
#         self.cb_1.setChecked(True)
#         pe = QPalette()
#         pe.setColor(QPalette.Window, Qt.white)
#         self.setPalette(pe)
#         self.setAutoFillBackground(True)
#
#         layout = QHBoxLayout()
#         layout.addWidget(self.cb_1)
#         layout.addWidget(self.cb_2)
#         self.setLayout(layout)

class initialSettingBlock(QGroupBox):
    def __init__(self):
        super(initialSettingBlock, self).__init__()
        self.__isExtSync = False
        self.cb_

class calibrationBlock(QGroupBox):
    def __init__(self):
        super(calibrationBlock, self).__init__()
        self.__isCali_a = False
        self.__isCali_w = False
        self.resize(320, 100)
        self.setWindowTitle('IMU calibration')
        # self.setTitle('enable')
        # self.setCheckable(True)
        self.cb_cali_w = QCheckBox('calibrate gyro')
        self.cb_cali_a = QCheckBox('calibrate accelerometer')
        self.cb_cali_w.setChecked(True)
        self.isCali_w = True
        self.cb_cali_a.stateChanged.connect(lambda: self.cbstate_connect(self.cb_cali_a))
        self.cb_cali_w.stateChanged.connect(lambda: self.cbstate_connect(self.cb_cali_w))

        layout = QVBoxLayout()
        layout.addWidget(self.cb_cali_w)
        layout.addWidget(self.cb_cali_a)
        self.setLayout(layout)

    def cbstate_connect(self, cb):
        if cb.text() == 'calibrate gyro':
            self.isCali_w = cb.isChecked()
        elif cb.text() == 'calibrate accelerometer':
            self.isCali_a = cb.isChecked()
        self.cali_status()

    def cali_status(self):
        cmn.print_debug(' \nmygui_serial: self.isChecked = %s' % self.isChecked(), PRINT_DEBUG)
        cmn.print_debug(' mygui_serial: self.isCali_w = %s' % self.isCali_w, PRINT_DEBUG)
        cmn.print_debug(' mygui_serial: self.isCali_a = %s' % self.isCali_a, PRINT_DEBUG)
        # if not self.isChecked():
        #     return False, False
        # else:
        #     return self.isCali_w, self.isCali_a
        return self.isCali_w, self.isCali_a

    @property
    def isCali_w(self):
        return self.__isCali_w

    @isCali_w.setter
    def isCali_w(self, isFlag):
        self.__isCali_w = isFlag
        # print("isCali_w: ", self.isCali_w)

    @property
    def isCali_a(self):
        return self.__isCali_a

    @isCali_a.setter
    def isCali_a(self, isFlag):
        self.__isCali_a = isFlag
        # print("isCali_a: ", self.isCali_a)


# class radioButtonBlock_2(QGroupBox):
#     def __init__(self, title='', name1='', name2=''):
#         super(radioButtonBlock_2, self).__init__()
#         self.setTitle(title)
#         self.__btn_status = None
#         self.rb1 = QRadioButton(name1)
#         self.rb2 = QRadioButton(name2)
#         self.rb1.setChecked(True)
#         self.btn_status = name1
#         self.rb1.toggled.connect(lambda: self.btnstate_connect(self.rb1))
#         self.rb2.toggled.connect(lambda: self.btnstate_connect(self.rb2))
#         pe = QPalette()
#         pe.setColor(QPalette.Window, Qt.white)
#         self.setPalette(pe)
#         self.setAutoFillBackground(True)
#         layout = QHBoxLayout()
#         layout.addWidget(self.rb1)
#         layout.addWidget(self.rb2)
#         self.setLayout(layout)
#
#     def btnstate_connect(self, btn):
#         if btn.isChecked():
#             self.btn_status = btn.text()
#
#     @property
#     def btn_status(self):
#         return self.__btn_status
#
#     @btn_status.setter
#     def btn_status(self, state):
#         self.__btn_status = state


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = calibrationBlock()
    main.show()
    app.exec_()
