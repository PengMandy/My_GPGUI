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
import matplotlib

matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, plot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pyqtgraph as pg
from myLib import common as cmn
from pyqtgraph import PlotWidget

PRINT_DEBUG = 1


# class pgGraph_1(QMainWindow):
#     def __init__(self):
#         super(pgGraph_1, self).__init__()
#         self.ax = PlotWidget()
#         self.setCentralWidget(self.ax)

# class pgGraph_2(QMainWindow):
#     def __init__(self):
#         super(pgGraph_2, self).__init__()
#         self.ax1 = PlotWidget()
#         self.ax2 = PlotWidget()
#
#         layout = QGridLayout()
#         layout.addWidget(self.ax1, 0, 0, 1, 1)
#         layout.addWidget(self.ax2, 1, 0, 1, 1)
#         win = QWidget()
#         win.setLayout(layout)
#         # self.setLayout(layout)
#         self.setCentralWidget(win)

class pgGraph_1(QMainWindow):
    def __init__(self, color="w", title="add title"):
        super(pgGraph_1, self).__init__()
        self.ax = None
        win = pg.GraphicsWindow()
        win.setBackground('k')
        pen = pg.mkPen(color=color, width=1)
        self.p = win.addPlot(title=title)
        self.ax = self.p.plot(pen=pen)
        self.setCentralWidget(win)


# class pgGraph_1_2(QMainWindow):
#     def __init__(self, color1="w", color2="w", title="add title"):
#         super(pgGraph_1_2, self).__init__()
#
#         win = pg.GraphicsWindow()
#         win.setBackground('k')
#         pen1 = pg.mkPen(color=color1, width=1)
#         pen2 = pg.mkPen(color=color2, width=1)
#         self.p = win.addPlot(title=title)
#         self.ax1 = self.p.plot(pen=pen1)
#         self.ax2 = self.p.plot(pen=pen2)
#         self.setCentralWidget(win)


class pgGraph_1_2(QMainWindow):
    def __init__(self, color1="w", color2="w", width1=1, width2=1, title="add title"):
        super(pgGraph_1_2, self).__init__()

        win = pg.GraphicsLayoutWidget()
        # win.setBackground((100, 10, 34))
        win.setBackground('k')
        pen1 = pg.mkPen(color=color1, width=width1)
        pen2 = pg.mkPen(color=color2, width=width2)
        self.p = win.addPlot(title=title)
        # print(type(win))
        # print(type(self.p))
        self.ax1 = self.p.plot(pen=pen1)
        self.ax2 = self.p.plot(pen=pen2)
        # print(type(self.ax1))
        self.setCentralWidget(win)


class pgGraph_2(QMainWindow):
    def __init__(self):
        super(pgGraph_2, self).__init__()

        win = pg.GraphicsWindow()
        win.setBackground('k')
        p1 = win.addPlot()
        p1.addLegend()
        self.ax1_1 = p1.plot()
        self.ax1_2 = p1.plot()
        self.ax1_3 = p1.plot()
        win.nextRow()
        p2 = win.addPlot()
        self.ax2_1 = p2.plot()
        self.ax2_2 = p2.plot()
        self.ax2_3 = p2.plot()

        self.setCentralWidget(win)


class mplGraph_1(QWidget):
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        super(mplGraph_1, self).__init__(parent)
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        canvas = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(canvas=canvas, parent=self)
        self.ax = self.fig.add_subplot(111)
        layout = QGridLayout()
        layout.addWidget(canvas, 0, 0, 2, 2)
        layout.addWidget(toolbar, 2, 0, 1, 1)
        self.setLayout(layout)


class mplGraph_2(QWidget):
    def __init__(self, width=10, height=10, dpi=100):
        super(mplGraph_2, self).__init__()
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        canvas = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(canvas=canvas, parent=None)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        layout = QGridLayout()
        layout.addWidget(canvas, 0, 0, 2, 2)
        layout.addWidget(toolbar, 2, 0, 1, 1)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication([])
    fig = mplGraph_1()
    fig.ax.plot([1,2,3,4,5], [5,5,5,5,10])
    fig.ax.clear()
    fig.show()
    app.exec_()
