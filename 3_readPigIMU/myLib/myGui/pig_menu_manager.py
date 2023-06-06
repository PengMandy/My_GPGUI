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


class pig_menu_manager:
    def __init__(self, menuBar, obj):
        self.pig_initial_setting_action = None
        self.pig_plot_action = None
        self.pig_allan_action = None
        self.pig_cali_action = None
        self.pig_para_action = None
        self.setting_menu = menuBar.addMenu("Setting")
        self.analysis_menu = menuBar.addMenu("Analysis")
        self.action_list(obj)

    def action_list(self, obj):
        self.pig_para_action = QAction("pig parameters", obj)
        self.pig_para_action.setShortcut("Ctrl+P")
        self.pig_para_action.setEnabled(False)
        self.pig_cali_action = QAction("pig calibration", obj)
        self.pig_cali_action.setShortcut("Ctrl+k")
        self.pig_cali_action.setEnabled(True)
        self.pig_initial_setting_action = QAction("pig initial setting", obj)
        self.pig_initial_setting_action.setShortcut("Ctrl+i")
        self.pig_initial_setting_action.setEnabled(True)
        self.setting_menu.addAction(self.pig_para_action)
        self.setting_menu.addAction(self.pig_cali_action)
        self.setting_menu.addAction(self.pig_initial_setting_action)

        self.pig_allan_action = QAction("Allan Deviation", obj)
        self.pig_allan_action.setShortcut("Ctrl+A")
        self.pig_plot_action = QAction("Plot Timing Data", obj)
        self.pig_plot_action.setShortcut("Ctrl+T")
        self.analysis_menu.addAction(self.pig_plot_action)
        self.analysis_menu.addAction(self.pig_allan_action)

    def action_trigger_connect(self, fn):
        self.pig_para_action.triggered.connect(fn[0])
        self.pig_cali_action.triggered.connect(fn[1])
        self.pig_plot_action.triggered.connect(fn[2])
        self.pig_allan_action.triggered.connect(fn[3])
        self.pig_initial_setting_action.triggered.connect(fn[4])

    def setEnable(self, open):
        self.pig_para_action.setEnabled(open)
        self.pig_cali_action.setEnabled(not open)
        self.pig_initial_setting_action.setEnabled(not open)