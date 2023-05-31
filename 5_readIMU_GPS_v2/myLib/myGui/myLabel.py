# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import sys

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


class logo(QLabel):
    def __init__(self, pic_path):
        super(logo, self).__init__()
        self.setStyleSheet('''QLabel{background-color: #3b234d}''')
        self.setAlignment(Qt.AlignCenter)
        self.setPixmap(QPixmap(pic_path))


class displayOneBlock(QGroupBox):
    def __init__(self, name='name', title_size=10, label_size=10):
        super(displayOneBlock, self).__init__()
        self.setTitle(name)
        self.setFont(QFont('', title_size))
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.yellow)
        pe.setColor(QPalette.Window, Qt.black)
        self.lb = QLabel()
        self.lb.setPalette(pe)
        self.lb.setFont(QFont('Arial', label_size))
        self.lb.setAutoFillBackground(True)
        self.lb.setText('buffer')

        layout = QVBoxLayout()
        layout.addWidget(self.lb)
        self.setLayout(layout)


class twoLabelBlock(QGroupBox):
    def __init__(self, title='', name1='', name2=''):
        super(twoLabelBlock, self).__init__()
        self.setTitle(title)
        self.setFont(QFont('', 10))
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.blue)
        # pe.setColor(QPalette.Window, Qt.black)
        self.lb1 = QLabel(name1)
        self.lb2 = QLabel(name2)
        self.lb1.setPalette(pe)
        self.lb1.setFont(QFont('Arial', 20))
        self.lb2.setFont(QFont('Arial', 15))
        self.layout()

    def layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.lb1)
        layout.addWidget(self.lb2)
        self.setLayout(layout)
        return self


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = twoLabelBlock(title='Progrss', name1='Status')
    w.show()
    app.exec_()
