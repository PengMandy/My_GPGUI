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


class checkBoxBlock_2(QGroupBox):
    def __init__(self, title='', name1='', name2=''):
        super(checkBoxBlock_2, self).__init__()
        self.setFont(QFont('Arial', 10))
        self.setTitle(title)
        self.cb_1 = QCheckBox(name1)
        self.cb_2 = QCheckBox(name2)
        self.cb_1.setChecked(True)
        # pe = QPalette()
        # pe.setColor(QPalette.Window, Qt.white)
        # self.setPalette(pe)
        # self.setAutoFillBackground(True)

        layout = QHBoxLayout()
        layout.addWidget(self.cb_1)
        layout.addWidget(self.cb_2)
        self.setLayout(layout)
