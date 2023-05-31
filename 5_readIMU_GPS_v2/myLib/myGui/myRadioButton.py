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


class radioButtonBlock_2(QGroupBox):
    def __init__(self, title='', name1='', name2='', rb1Set=True):
        super(radioButtonBlock_2, self).__init__()
        self.setFont(QFont('Arial', 10))
        self.setTitle(title)
        self.__btn_status = None
        self.rb1 = QRadioButton(name1)
        self.rb2 = QRadioButton(name2)
        self.rb1.setChecked(rb1Set)
        self.rb2.setChecked(not rb1Set)
        if rb1Set:
            self.btn_status = name1
        else:
            self.btn_status = name2
        self.rb1.toggled.connect(lambda: self.btnstate_connect(self.rb1))
        self.rb2.toggled.connect(lambda: self.btnstate_connect(self.rb2))
        # pe = QPalette()
        # pe.setColor(QPalette.Window, Qt.white)
        # self.setPalette(pe)
        # self.setAutoFillBackground(True)
        layout = QHBoxLayout()
        layout.addWidget(self.rb1)
        layout.addWidget(self.rb2)
        self.setLayout(layout)

    def btnstate_connect(self, btn):
        if btn.isChecked():
            self.btn_status = btn.text()

    @property
    def btn_status(self):
        return self.__btn_status

    @btn_status.setter
    def btn_status(self, state):
        self.__btn_status = state


# class filter_rb(QRadioButton):
#     def __init__(self, name=''):
#         super(filter_rb, self).__init__()
#
#         # self.rb = QRadioButton(name)
#         self.setFont(QFont('Arial', 10))
#         self.setGeometry(200, 150, 120, 40)
#         self.setStyleSheet("QRadioButton::indicator"
#                                         "{"
#                                         "width : 50px;"
#                                         "height : 50px;"
#                                         "}")


class filter_rb(QGroupBox):
    def __init__(self, title=''):
        super(filter_rb, self).__init__()
        self.setFont(QFont('Arial', 10))
        self.setTitle(title)
        rb = QRadioButton()
        layout = QHBoxLayout()
        layout.addWidget(rb)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = radioButtonBlock_2('Sync Mode', 'INT', 'EXT')
    w.show()
    app.exec_()
