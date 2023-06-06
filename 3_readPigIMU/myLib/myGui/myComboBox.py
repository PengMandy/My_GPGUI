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
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from myLib import common as cmn

DEBUG_EN = 1


class comboGroup_1(QGroupBox):
    default_Item_qt = pyqtSignal(object)

    def __init__(self, title='', cb_name=''):
        super(comboGroup_1, self).__init__()
        self.setTitle(title)
        self.cb = QComboBox()
        self.cb.setProperty('name', cb_name)
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.cb)
        self.setLayout(layout)

    def addItem(self, item=[]):
        for i in item:
            self.cb.addItem(i)
        self.cb.setCurrentText(item[0])
        self.default_Item_qt.emit(self.cb.currentText())
        # print('com: ', self.cb.currentText())

    def getText_connect(self, fn):
        self.cb.currentIndexChanged.connect(lambda: fn(self.cb))

    def rt(self):
        return self


def testfn(i):
    cmn.print_debug('name: %s' % i.property('name'), DEBUG_EN)
    cmn.print_debug('key: %s' % i.currentText(), DEBUG_EN)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = comboGroup_1('test', 'select')
    w.rt()
    w.addItem(['A', 'B'])
    w.getText_connect(testfn)
    w.show()
    app.exec_()
