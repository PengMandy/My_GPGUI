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
import os, sys
import pandas as pd
import time


class progress_bar_with_read_allan(QGroupBox):
    is_load_done_qt = pyqtSignal(bool)
    data_qt = pyqtSignal(object)

    def __init__(self, title=''):
        super(progress_bar_with_read_allan, self).__init__()
        self.setTitle(title)
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.blue)
        # line editor
        self.file_le = QLineEdit('tt.txt')
        self.tp_le = QLineEdit()
        self.tp_le.setFixedWidth(100)
        self.tp_le.setProperty('name', 'tp')
        self.tauarray_le = QLineEdit('')
        self.tauarray_le.setProperty('name', 'tau')
        # button
        self.read_bt = QPushButton('read')
        # label
        self.tp_lb = QLabel('t1, t2 : insert 5 points between t1 and t2 seconds')
        self.tp_lb.setPalette(pe)
        self.tp_lb.setFixedWidth(100)
        self.tp_lb.setFont(QFont('Arial', 12))
        self.tp_lb.setFixedWidth(500)
        self.status_lb = QLabel()

        self.pbar_text = ''
        self.read_bt.setFixedWidth(130)
        self.file_le.setFixedWidth(150)
        self.filename = self.file_le.text()
        self.pbar = QProgressBar()
        self.pbar.setFixedWidth(300)
        self.connect()
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.read_bt, 0, 0, 1, 1)
        layout.addWidget(self.file_le, 1, 0, 1, 1)
        layout.addWidget(self.status_lb, 0, 7, 1, 1)
        layout.addWidget(self.pbar, 1, 7, 1, 3)
        layout.addWidget(self.tp_le, 0, 1, 1, 1)
        layout.addWidget(self.tp_lb, 0, 2, 1, 5)
        layout.addWidget(self.tauarray_le, 1, 1, 1, 6)
        self.setLayout(layout)

    def connect(self):
        self.file_le.editingFinished.connect(self.set_filename)
        self.read_bt.clicked.connect(self.read_btn)

    def set_filename(self):
        self.filename = self.file_le.text()
        print(self.file_le.text())

    def set_filename_ext(self, name):
        self.file_le.setText(name)
        self.filename = name

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, name):
        self.__filename = name

    @property
    def pbar_text(self):
        return self.__pbar_text

    @pbar_text.setter
    def pbar_text(self, text):
        self.__pbar_text = text
        self.status_lb.setText(text)
        # print('pbar_text: ', self.status_lb.setText(text))
        # print('my progress bar.pbar_text: ', self.pbar_text)

    def read_btn(self):
        self.readData()
        # self.readData_fast()

    def readData_fast(self):
        print('read_fast begin: ')
        t1 = time.perf_counter()
        # Var = pd.read_csv(self.filename, comment='#')
        # Var = pd.read_csv(self.filename, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0,
        #                   chunksize=None)
        Var = pd.read_csv(self.filename, comment='#', skiprows=0, chunksize=None)
        t2 = time.perf_counter()
        self.data_qt.emit(Var)
        # print(Var)
        print('read done: ', t2 - t1)

    def readData(self, chunksize=6000, row_len=20, skiprows=2):
        print('read_chunk begin: ')
        self.is_load_done_qt.emit(False)
        t1 = time.perf_counter()
        nrows = row_len - 1
        total_data_len = self.find_data_length(self.filename, nrows, row_len, skiprows)
        chunksize = int(total_data_len / 100)
        df = []
        # for chunk in pd.read_csv(self.filename, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0,
        #                          chunksize=chunksize):
        for chunk in pd.read_csv(self.filename, comment='#', skiprows=0, chunksize=chunksize):
            df.append(chunk)
            current_data_len = len(df) * chunksize
            self.updatePbar(current_data_len, total_data_len)
        data = pd.concat((f for f in df))
        t2 = time.perf_counter()
        print('read done: ', t2 - t1)
        self.data_qt.emit(data)
        self.is_load_done_qt.emit(True)
        self.updatePbar(total_data_len, total_data_len)

    def find_data_length(self, file, nrows, row_len, skiprows):
        temp = pd.read_csv(file, sep=r'\s*,\s*', engine='python', comment='#', skiprows=skiprows, nrows=nrows)
        file_size = os.path.getsize(file)
        block_size = len(temp.to_csv(index=False)) * 1.05
        total_data_len = int(file_size / block_size) * row_len
        return total_data_len

    def updatePbar(self, now, total):
        # print(round(now / total, 2))
        self.pbar.setValue(int(now * 100 / total))

    def inst(self):
        return self


class progress_bar_with_read(QGroupBox):
    is_load_done_qt = pyqtSignal(bool)
    data_qt = pyqtSignal(object)

    def __init__(self, title=''):
        super(progress_bar_with_read, self).__init__()
        self.setTitle(title)
        self.file_le = QLineEdit('tt.txt')
        self.read_bt = QPushButton('read')
        self.status_lb = QLabel()
        self.pbar_text = ''
        self.read_bt.setFixedWidth(130)
        self.file_le.setFixedWidth(150)
        self.filename = self.file_le.text()
        self.pbar = QProgressBar()
        self.pbar.setFixedWidth(600)
        self.connect()
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.read_bt, 0, 0, 1, 1)
        layout.addWidget(self.file_le, 1, 0, 1, 1)
        layout.addWidget(self.status_lb, 0, 1, 1, 1)
        layout.addWidget(self.pbar, 1, 1, 1, 3)
        self.setLayout(layout)

    def connect(self):
        self.file_le.editingFinished.connect(self.set_filename)
        self.read_bt.clicked.connect(self.read_btn)

    def set_filename(self):
        self.filename = self.file_le.text()
        print(self.file_le.text())

    def set_filename_ext(self, name):
        self.file_le.setText(name)
        self.filename = name

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, name):
        self.__filename = name

    @property
    def pbar_text(self):
        return self.__pbar_text

    @pbar_text.setter
    def pbar_text(self, text):
        self.__pbar_text = text
        self.status_lb.setText(text)
        # print('pbar_text: ', self.status_lb.setText(text))
        # print('my progress bar.pbar_text: ', self.pbar_text)

    def read_btn(self):
        self.readData()
        # self.readData_fast()

    def readData_fast(self):
        print('read_fast begin: ')
        t1 = time.perf_counter()
        # Var = pd.read_csv(self.filename, comment='#')
        # Var = pd.read_csv(self.filename, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0,
        #                   chunksize=None)
        Var = pd.read_csv(self.filename, comment='#', skiprows=0, chunksize=None)
        t2 = time.perf_counter()
        self.data_qt.emit(Var)
        # print(Var)
        print('read done: ', t2 - t1)

    def readData(self, chunksize=6000, row_len=20, skiprows=2):
        print('read_chunk begin: ')
        self.is_load_done_qt.emit(False)
        t1 = time.perf_counter()
        nrows = row_len - 1
        total_data_len = self.find_data_length(self.filename, nrows, row_len, skiprows)
        chunksize = int(total_data_len / 100)
        df = []
        # for chunk in pd.read_csv(self.filename, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0,
        #                          chunksize=chunksize):
        for chunk in pd.read_csv(self.filename, comment='#', skiprows=0, chunksize=chunksize):
            df.append(chunk)
            current_data_len = len(df) * chunksize
            self.updatePbar(current_data_len, total_data_len)
        data = pd.concat((f for f in df))
        t2 = time.perf_counter()
        print('read done: ', t2 - t1)
        self.data_qt.emit(data)
        self.is_load_done_qt.emit(True)
        self.updatePbar(total_data_len, total_data_len)

    def find_data_length(self, file, nrows, row_len, skiprows):
        temp = pd.read_csv(file, sep=r'\s*,\s*', engine='python', comment='#', skiprows=skiprows, nrows=nrows)
        file_size = os.path.getsize(file)
        block_size = len(temp.to_csv(index=False)) * 1.05
        total_data_len = int(file_size / block_size) * row_len
        return total_data_len

    def updatePbar(self, now, total):
        # print(round(now / total, 2))
        self.pbar.setValue(int(now * 100 / total))

    def inst(self):
        return self


class progress_bar_with_read_thread(QThread):
    is_load_done_qt = pyqtSignal(bool, object)
    data_qt = pyqtSignal(object)

    def __init__(self, title=''):
        super(progress_bar_with_read_thread, self).__init__()
        self.filename = '0619.txt'
        self.is_load_done = False
        self.win = QGroupBox()
        self.win.setTitle(title)
        self.status_lb = QLabel()
        self.pbar_text = ''
        self.pbar = QProgressBar()
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.status_lb, 0, 0, 1, 1)
        layout.addWidget(self.pbar, 1, 0, 1, 3)
        self.win.setLayout(layout)

    def inst(self):
        return self.win

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, name):
        self.__filename = name
        # print('my progress bar.filename: ', self.filename)

    @property
    def pbar_text(self):
        return self.__pbar_text

    @pbar_text.setter
    def pbar_text(self, text):
        self.__pbar_text = text
        self.status_lb.setText(text)

    def run(self):
        self.started.emit()
        self.readData()

    def readData(self, chunksize=60000, row_len=20, skiprows=2):
        print('read_chunk begin: ')
        t1 = time.perf_counter()
        nrows = row_len - 1
        total_data_len = self.find_data_length(self.filename, nrows, row_len, skiprows)
        print('total_data_len: ', total_data_len)
        chunksize = int(total_data_len / 100)
        # chunksize = 10000
        df = []
        # for chunk in pd.read_csv(self.filename, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0,
        #                          chunksize=chunksize):
        for chunk in pd.read_csv(self.filename, comment='#', skiprows=0, chunksize=chunksize):
            df.append(chunk)
            current_data_len = len(df) * chunksize
            self.updatePbar(current_data_len, total_data_len)
        self.updatePbar(total_data_len, total_data_len)
        data = pd.concat((f for f in df))
        self.finished.emit()
        self.data_qt.emit(data)
        t2 = time.perf_counter()
        print('read done: ', t2 - t1)

    def find_data_length(self, file, nrows, row_len, skiprows):
        temp = pd.read_csv(file, sep=r'\s*,\s*', engine='python', comment='#', skiprows=skiprows, nrows=nrows)
        file_size = os.path.getsize(file)
        block_size = len(temp.to_csv(index=False)) * 1.05
        total_data_len = int(file_size / block_size) * row_len
        return total_data_len

    def updatePbar(self, now, total):
        self.pbar.setValue(int(now * 100 / total))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # w = progress_bar_with_read_thread('')
    # w.filename = '0619.txt'
    # w.inst().show()
    # w.start()

    w = progress_bar_with_read_allan('')
    w.inst()
    w.show()

    app.exec_()
