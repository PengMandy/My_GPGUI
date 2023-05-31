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
import sys

sys.path.append("../")
from PyQt5.QtWidgets import *
import sys
from myLib.myGui.graph import *
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *
from myLib.myGui.myLineEdit import *
from myLib.myGui.myCheckBox import *
from myLib.myGui.myRadioButton import *
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from myLib.myGui.pig_menu_manager import pig_menu_manager


class pigImuWidget(QWidget):

    def __init__(self, menuBar):
        super(pigImuWidget, self).__init__()
        self.initUI()
        self.pig_menu = pig_menu_manager(menuBar)

    def initUI(self):
        self.usb = usbConnect_auto()
        self.read_bt = QPushButton("read")
        self.read_bt.setFont(QFont('Arial', 15))
        self.read_bt.setEnabled(False)
        self.stop_bt = QPushButton("stop")
        self.stop_bt.setEnabled(False)
        self.stop_bt.setFont(QFont('Arial', 15))
        self.save_block = dataSaveBlock_noExt('Enter File Path')
        # self.para_block = lineEditBlock('parameter configuration file', le_name='parameters_SP10')
        self.gpstime_lb = displayOneBlock('Date (GPS Date in UTC)', label_size=20)
        self.buffer_lb = displayOneBlock('Buffer Size_SP10')
        self.buffer_lb_2 = displayOneBlock('Buffer Size_SP11')
        self.buffer_lb_3 = displayOneBlock('Buffer Size_SP13')
        self.pd_temp_lb = displayOneBlock('PD Temp_SP10')
        self.pd_temp_lb_2 = displayOneBlock('PD Temp_SP11')
        self.pd_temp_lb_3 = displayOneBlock('PD Temp_SP13')
        self.data_rate_lb = displayOneBlock('Data Rate_SP10')
        self.data_rate_lb_2 = displayOneBlock('Data Rate_SP11')
        self.data_rate_lb_3 = displayOneBlock('Data Rate_SP13')
        self.logo_lb = logo('./aegiverse_logo_bk.jpg')
        self.date_rb = radioButtonBlock_2('date type', 'PC', 'GPS')
        # self.plot1_showWz_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        # self.plot1_unit_rb = radioButtonBlock_2('Unit', 'dph', 'dps')
        # self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG_WZ VS MEMS_WZ")
        self.plot1 = pgGraph_1(color=(255, 0, 0), title="FOG_WX [DPS]")
        self.plot2 = pgGraph_1(color=(255, 0, 0), title="FOG_WY [DPS]")
        self.plot3 = pgGraph_1(color=(255, 0, 0), title="FOG_WZ [DPS]")
        self.plot4 = pgGraph_1(color=(255, 0, 0), title="AX [g]")
        self.plot5 = pgGraph_1(color=(255, 0, 0), title="AY [g]")
        self.plot6 = pgGraph_1(color=(255, 0, 0), title="AZ [g]")

        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 2, 8)
        layout.addWidget(self.read_bt, 0, 8, 1, 1)
        layout.addWidget(self.stop_bt, 0, 9, 1, 1)
        layout.addWidget(self.save_block, 0, 10, 2, 5)
        layout.addWidget(self.gpstime_lb, 3, 6, 2, 9)
        layout.addWidget(self.buffer_lb, 2, 0, 1, 2)
        layout.addWidget(self.buffer_lb_2, 3, 0, 1, 2)
        layout.addWidget(self.buffer_lb_3, 4, 0, 1, 2)
        layout.addWidget(self.pd_temp_lb, 2, 2, 1, 2)
        layout.addWidget(self.pd_temp_lb_2, 3, 2, 1, 2)
        layout.addWidget(self.pd_temp_lb_3, 4, 2, 1, 2)
        layout.addWidget(self.data_rate_lb, 2, 4, 1, 2)
        layout.addWidget(self.data_rate_lb_2, 3, 4, 1, 2)
        layout.addWidget(self.data_rate_lb_3, 4, 4, 1, 2)
        layout.addWidget(self.logo_lb, 0, 15, 5, 5)
        # layout.addWidget(self.para_block, 0, 4, 1, 1)
        layout.addWidget(self.date_rb, 2, 6, 1, 2)
        '''#### plot ###'''
        layout.addWidget(self.plot1, 5, 0, 6, 10)
        # layout.addWidget(self.plot1_showWz_cb, 1, 2, 1, 2)
        # layout.addWidget(self.plot1_unit_rb, 1, 0, 1, 2)
        layout.addWidget(self.plot2, 11, 0, 6, 10)
        layout.addWidget(self.plot3, 17, 0, 6, 10)
        layout.addWidget(self.plot4, 5, 10, 6, 10)
        layout.addWidget(self.plot5, 11, 10, 6, 10)
        layout.addWidget(self.plot6, 17, 10, 6, 10)

        self.setLayout(layout)

    def setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(en)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pigImuWidget()

    w.show()
    app.exec_()
