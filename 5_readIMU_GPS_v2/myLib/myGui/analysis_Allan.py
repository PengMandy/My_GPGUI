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

import sys

sys.path.append("../../")
import numpy as np
import pandas as pd
import time
from myLib.myGui import graph
from myLib.myGui import myLabel
from myLib.myGui import myProgressBar
from myLib.myGui import myComboBox
import myLib.common as cmn
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import matplotlib.pyplot as plt


class analysis_allan_widget(QWidget):
    def __init__(self, key_item=['fog', 'wx', 'wy', 'wz']):
        # logging.basicConfig(level=100)
        super(analysis_allan_widget, self).__init__()
        self.tau0 = 1
        self.tauArray = None
        self.__time = None
        self.data = None
        self.setWindowTitle('Allen Variance Analysis')
        self.resize(900, 900)
        self.dev = np.empty(0)  # Create empty array to store the output.
        self.actualTau = np.empty(0)
        self.allan = allan_dev()
        # add widget
        self.cb = myComboBox.comboGroup_1('select data', 'select')
        self.pbar = myProgressBar.progress_bar_with_read_allan('test')
        self.datahub = cmn.data_hub_manager()
        self.allan_plot = graph.mplGraph_1()
        self.cal_bt = QPushButton('cal')
        self.cal_bt.setEnabled(False)
        # end of add widget
        self.linkfunction()
        self.cb.addItem(key_item)
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.cal_bt, 0, 0, 1, 1)
        layout.addWidget(self.cb, 1, 0, 1, 1)
        layout.addWidget(self.pbar.inst(), 0, 1, 2, 5)
        layout.addWidget(self.allan_plot, 2, 0, 10, 10)
        self.setLayout(layout)

    def linkfunction(self):
        self.cb.getText_connect(self.datahub.connect_combobox)
        self.cal_bt.clicked.connect(self.cal_allan_dev)
        self.pbar.data_qt.connect(self.store_data)
        self.pbar.is_load_done_qt.connect(self.set_is_load_done_connect)
        self.allan.is_allan_done_qt.connect(self.set_is_allan_done_connect)
        self.cb.default_Item_qt.connect(self.set_default_key)
        self.pbar.tauarray_le.editingFinished.connect(
            lambda: self.set_tau_array(self.pbar.tauarray_le))
        self.pbar.tp_le.editingFinished.connect(lambda: self.set_tau_array(self.pbar.tp_le))
        self.allan.progress_qt.connect(self.update_progress_bar)
        self.allan.allan_qt.connect(self.plot)
        self.allan.finish_qt.connect(self.fit_data)

    def cal_tau_array(self):
        t = np.array(self.__time)
        datalength = len(t)
        self.allan.datalength = datalength
        tau0 = round((t[-1] - t[0]) / (datalength - 1), 3)
        self.tau0 = tau0
        self.allan.tau0 = tau0
        print('cal_tau_array.self.tau0: ', self.tau0)
        rate = int(1 / tau0)
        m_max = int(np.floor((datalength - 1) / 2))
        print('cal_tau_array.m_max: ', m_max, end=', ')
        print(np.log10(m_max))
        n = np.logspace(0, np.log10(m_max), 10, dtype=int)
        print('cal_tau_array.n: ', n)
        n = np.append(n, rate)
        tauArray = np.sort(n)
        self.tauArray = [int(i) for i in tauArray]  # this line modify the data type of tauarray, do not omit.
        self.allan.tauArray = self.tauArray
        print('cal_tau_array.self.tauArray: ', self.tauArray)
        self.update_tauarray_le_text(self.tauArray)
        # self.pbar.tauarray_le.setText(str(self.tauArray*tau0))
        # self.tauarray_qt.emit(self.tauArray)

    @property
    def tau0(self):
        return self.__tau0

    @tau0.setter
    def tau0(self, tau0):
        self.__tau0 = tau0

    def set_tau_array(self, value):
        # print(value.property('name'))
        le_name = value.property('name')
        if le_name == 'tau':
            temp = value.text().strip('[]').split(',')
            temp = [np.floor(float(i) / self.tau0) for i in temp]
            temp = np.array(temp, dtype=int)
            self.tauArray = np.unique(temp)
            self.tauArray = [int(i) for i in self.tauArray]
            self.allan.tauArray = self.tauArray
            print('set_tau_array.tau_le: ', self.tauArray, type(self.tauArray[0]))

        elif le_name == 'tp':
            if bool(value.text()):
                try:
                    temp = value.text().strip('[]').split(',')
                    temp = [np.floor(float(i) / self.tau0) for i in temp]
                    temp = np.array(temp, dtype=int)
                    tp1 = temp[0]
                    tp2 = temp[1]
                    n = np.logspace(np.log10(tp1), np.log10(tp2), 5, dtype=int)
                    self.tauArray = np.unique(np.append(self.tauArray, n))
                    self.tauArray = [int(i) for i in self.tauArray]
                    self.allan.tauArray = self.tauArray
                    self.update_tauarray_le_text(self.tauArray)
                    print('set_tau_array.tp_le: ', self.tauArray, type(self.tauArray[0]))

                except ValueError:
                    print('ValueError')

    def update_tauarray_le_text(self, tauarray):
        tauarray = [round(i * self.tau0, 2) for i in tauarray]
        self.pbar.tauarray_le.setText(str(tauarray))

    def set_default_key(self, key):
        self.datahub.key = key

    def store_data(self, data=None):
        self.__time = data['time']
        self.datahub.store_df_data(data)
        self.cal_tau_array()

    def set_is_load_done_connect(self, done):
        self.cal_bt.setEnabled(done)
        if done:
            self.pbar.pbar_text = 'loading data: finish'
        else:
            self.pbar.pbar_text = 'loading data'

    def set_is_allan_done_connect(self, done):
        if done:
            self.pbar.pbar_text = 'calculating Allan: finish'
        else:
            self.pbar.pbar_text = 'calculating Allan'

    def update_progress_bar(self, idx, total):
        self.pbar.updatePbar(idx, total)

    def cal_allan_dev(self):
        # print(self.datahub.switch_df_data())
        self.allan.data = self.datahub.switch_df_data()
        self.allan.start()

    def fit_data(self, tau, dev):
        ax = self.allan_plot.ax
        idx_bias = self.findBias(tau, dev)
        if idx_bias is not None:
            bias = dev[idx_bias] * 3600
            self.allan_plot.ax.loglog(tau, [bias] * len(tau), color='green', linestyle='--', linewidth=2)
            ax.text(0.8, 0.7, 'bias stability: ' + str(round(bias, 2)) + '$^\circ$/hr', ha='left', va='center',
                    transform=ax.transAxes,
                    color='k')

        idx_arw = np.where(np.abs(tau-1) < 0.005)[0][0]
        # print('tau-1: ', tau - 1)
        # print('idx_arw: ', idx_arw)
        x = np.log10(tau[0:idx_arw + 1])
        y = np.log10(dev[0:idx_arw + 1])
        a, b = np.polyfit(x, y, 1)
        arw = (10 ** b * 3600) / 60
        # plot fitted line
        if idx_bias is not None:
            idx_arw_max = idx_bias
        else:
            idx_arw_max = len(tau)
        self.allan_plot.ax.loglog(tau[0:idx_arw_max], 10 ** (a * np.log10(tau[0:idx_arw_max]) + b) * 3600, color='b',
                                  linestyle='--', linewidth=2)

        ax.text(0.8, 0.9, 'line fitting: ' + str(round(a, 2)) + 'x + ' + str(round(b, 2)), ha='left', va='center',
                transform=ax.transAxes, color='b')
        ax.text(0.8, 0.8, 'ARW: ' + str(round(arw, 4)) + '$^\circ$/' + r'$\sqrt{hr}$', ha='left', va='center',
                transform=ax.transAxes, color='g')

        self.allan_plot.fig.canvas.draw()
        # print(a, b, arw)
        # print(bias)

    def findBias(self, tau, dev):
        size = len(tau)
        tau2 = tau[1:size]
        dev2 = dev[1:size]
        dx = tau2 - tau[0:size - 1]
        dy = dev2 - dev[0:size - 1]
        slope = dy / dx
        # print(slope)
        try:
            idx = np.where(slope > 0)[0][0]
            return idx
            # return np.log10(dev[idx])
        except IndexError:
            logger.info('no bias instability value.')
            return None

    def plot(self, tau, dev):
        self.allan_plot.ax.clear()
        self.allan_plot.ax.loglog(tau, dev * 3600, 'k-*')  # convert unit to dph
        self.plot_control()
        self.allan_plot.fig.canvas.draw()

    def plot_control(self):
        ax = self.allan_plot.ax
        ax.set_xlabel('s')
        ax.set_ylabel('Degree / hour')
        ax.xaxis.label.set_size(14)
        ax.yaxis.label.set_size(14)
        ax.grid(True)


class allan_dev(QThread):
    allan_qt = pyqtSignal(object, object)
    finish_qt = pyqtSignal(object, object)
    # tauarray_qt = pyqtSignal(object)
    progress_qt = pyqtSignal(int, int)
    is_allan_done_qt = pyqtSignal(bool)

    def __init__(self):
        super(allan_dev, self).__init__()
        self.__tau0 = None
        self.__datalength = None
        self.__tauArray = None
        self.__data = None

    @property
    def datalength(self):
        return self.__datalength

    @datalength.setter
    def datalength(self, len):
        self.__datalength = len
        print('Allan.datalength setter: ', self.datalength)

    @property
    def tauArray(self):
        return self.__tauArray

    @tauArray.setter
    def tauArray(self, tau):
        self.__tauArray = tau
        print('Allan.tauArray setter: ', self.tauArray)

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data
        print('Allan.data setter: ', self.data)

    @property
    def tau0(self):
        return self.__tau0

    @tau0.setter
    def tau0(self, tau0):
        self.__tau0 = tau0
        print('Allan.tau0 setter: ', self.tau0)

    def run(self):
        self.is_allan_done_qt.emit(False)
        theta = tuple(np.cumsum(np.array(self.data)) * self.tau0)
        dev = np.array([])  # Create empty array to store the output.
        actualTau = np.array([])
        print('run')
        # progress_bar_total = len(self.tauArray)
        # progress_bar_current = 0
        # self.progress_qt.emit(progress_bar_current, progress_bar_total)
        pbar_total = len(self.tauArray)
        pbar_now = 0
        print(pbar_total)
        for n in self.tauArray:
            self.progress_qt.emit(pbar_now, pbar_total)
            currentSum = 0  # Initialize the sum
            tlp_s = time.perf_counter()
            # data = self.getdata()
            for j in range(0, self.datalength - 2 * n):
                currentSum = (theta[j + 2 * n] - 2 * theta[j + n] + theta[j]) ** 2 + currentSum
            tlp_e = time.perf_counter()
            print('n= ', n, end=', ')
            print(self.datalength - 2 * n, end=', ')
            print(round((tlp_e - tlp_s), 2))
            devAtThisTau = currentSum / (
                    2 * n ** 2 * self.tau0 ** 2 * (self.datalength - 2 * n))  # Divide by the coefficient
            dev = np.append(dev, np.sqrt(devAtThisTau))
            actualTau = np.append(actualTau, n * self.tau0)
            # progress_bar_current += 1
            # self.progress_qt.emit(progress_bar_current, progress_bar_total)
            self.allan_qt.emit(actualTau, dev)
            pbar_now += 1
        # end of for loop
        self.finish_qt.emit(actualTau, dev)
        self.is_allan_done_qt.emit(True)
        self.progress_qt.emit(pbar_total, pbar_total)
    # end of run()


class adj_tau_widget(QGroupBox):
    def __init__(self):
        super(adj_tau_widget, self).__init__()
        self.setFont(QFont('Arial', 10))
        self.setTitle('Adjust Tau Array')
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.blue)
        # pe.setColor(QPalette.Window, Qt.black)
        self.read_bt = QPushButton('Read File')
        self.read_bt.setProperty('name', 'read_bt')
        qssStyle = '''QPushButton[name='read_bt']{background-color:#F9F900}'''
        self.setStyleSheet(qssStyle)
        self.file_le = QLineEdit('0616_long.txt')
        self.tp_le = QLineEdit()
        # self.tp_le.setAutoFillBackground(True)
        # self.tp_le.setPalette(pe)
        self.tp_le.setFixedWidth(100)
        self.tp_lb = QLabel(' set: t1, t2, ex: 5.1, 10.2 insert 5 points between 5.1 and 10.2 seconds')
        # self.tp_lb.setAutoFillBackground(True)
        self.tp_lb.setPalette(pe)
        self.tp_lb.setFixedWidth(100)
        self.tp_lb.setFont(QFont('Arial', 12))

        self.tauarray_le = QLineEdit('')
        self.tp_lb.setFixedWidth(500)
        self.tp_le.setProperty('name', 'tp')
        self.tauarray_le.setProperty('name', 'tau')
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.read_bt, 0, 0, 1, 1)
        layout.addWidget(self.tp_le, 0, 1, 1, 1)
        layout.addWidget(self.tp_lb, 0, 2, 1, 5)
        layout.addWidget(self.file_le, 1, 0, 1, 1)
        layout.addWidget(self.tauarray_le, 1, 1, 1, 6)
        self.setLayout(layout)
        return self


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = analysis_allan_widget()
    # w = adj_tau_widget()
    w.show()
    app.exec_()
