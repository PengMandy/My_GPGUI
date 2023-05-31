# myGui 基本使用方法


- [myGui 基本使用方法](#mygui-基本使用方法)
  - [Tutorial](#tutorial)
  - [固定使用方式](#固定使用方式)
  - [Class QtWidgets](#class-qtwidgets)
  - [Class QWidget](#class-qwidget)
  - [class mplGraph_1 & mplGraph_2](#class-mplgraph_1--mplgraph_2)
    - [靜態繪圖](#靜態繪圖)
    - [動態繪圖](#動態繪圖)
  - [pytgraph](#pytgraph)
  - [USB 下拉式選單使用方法](#usb-下拉式選單使用方法)
  - [pig_menu_manager](#pig_menu_manager)

## Tutorial
https://build-system.fman.io/pyqt5-tutorial

https://www.pythonguis.com/tutorials/plotting-matplotlib/
## 固定使用方式

```python
from PyQt5.QtWidgets import QApplication

'''
code here
'''

if __name__ == "__main__"
app = QApplication([])
app.exec_()
```


## Class QtWidgets
幾乎所有QtGUI使用到的類別都來自此類別
```commandline
from PyQt5.QtWidgets import QApplication, QWidget, QLabel...
```

## Class QWidget 
QWidget 為所以QtGUI類別之容器，一般會先宣告一個名為window的
物件，之後其他的GUI類別會以window.setLayout()形式加到
window裡面。

直接使用:

```python
window = QWidget()
window.show()
```

或是由自己定義類別繼承:
```python
class myWidget(QWidget)
    
obj = myWidget(
obj.show()
)
```

## class mplGraph_1 & mplGraph_2
使用 matplotlib, 使用時先建立類別物件

```python
fig2 = mplGraph_2()
```

### 靜態繪圖
```python
if __name__ == '__main__':
    app = QApplication([])
    fig2 = mplGraph_2()
    fig2.ax1.plot([1, 2, 3])
    fig2.ax2.plot([1, 2, 5])
    fig2.show()
    app.exec_()
```

### 動態繪圖

```python
    def plotdata(self, wz):
        self.top.plot.ax.clear()
        self.wzz = np.append(self.wzz, wz)
        if len(self.wzz) > 1000:
            self.wzz = self.wzz[50:-1]
        print(len(self.wzz))
        print(self.act.readInputBuffer())
        self.top.plot.ax.plot(self.wzz)
        self.top.plot.fig.canvas.draw()
```


## pytgraph

https://www.pythonguis.com/tutorials/plotting-pyqtgraph/



## USB 下拉式選單使用方法
create: 2022/05/26

1. widget:

```python
from myLib.myGui.mygui_serial import *

# 宣告類別
self.usb = usbConnect()
```



2. main:

```python
from myLib.mySerial.Connector import Connector
from memsImu_Widget import memsImuWidget as TOP


def __init__(self):
    self.__portName = None
    self.__connector = Connector()
    self.top = TOP()
    self.linkfunciton()


def linkfunciton(self):
    # 按下後更新連接的port
    self.top.usb.bt_update.clicked.connect(self.updateComPort)
    # 從comboBox選擇想要連接的port
    self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
    # 按下後連接port
    self.top.usb.bt_connect.clicked.connect(self.connect)
    # 按下後段開連接的port
    self.top.usb.bt_disconnect.clicked.connect(self.disconnect)


# 使用定義在class Connector裡的 portList() 方法, 會回傳目前連接的port數量與資
# 訊，接著將回傳丟入定義在usbConnect()裡的 addPortItems() 方法，將port資訊加入comboBox裡。
def updateComPort(self):
    portNum, portList = self.__connector.portList()
    self.top.usb.addPortItems(portNum, portList)


# 使用定義在usbConnect()裡的 selectPort() 方法，將comboBox目前選中的port資訊
# 取出並顯示在label上。回傳為選中的port name，存在類別變數 self.__portName上。
def selectComPort(self):
    self.__portName = self.top.usb.selectPort()


# 將在__init__裡宣告的Connector物件 self.__connector 與 self.__portName 丟
# 入定義在act的connect方法，此方法會對這被丟入的物件與portName來打開serial port，若打開
# 成功會回傳True，把回傳丟入定義在usbConnect()裡的updateStatusLabel()方法，此
# 方法會針對port 是否開成功來enable or disable對應的開關。
def connect(self):
    is_open = self.act.connect(self.__connector, self.__portName, 230400)
    self.top.usb.updateStatusLabel(is_open)

# 斷開port連接，使用定義在act的disconnect()方法，一樣使用updateStatusLabel()，把is_open丟進去來控制button
def disconnect(self):
    is_open = self.act.disconnect()
    self.top.usb.updateStatusLabel(is_open)
```


## pig_menu_manager

此 class 用來產生 readPig 所要用到的 meanu, 定義:

```python
def __init__(self, menu, obj)

#使用前需在 main 先宣告 menuBar() 物件後丟入，obj 為 QMainWindow 之物件:

self.menu = self.menuBar()
self.pig_menu = pig_menu_widget(self.menu, self)

```

```python
def action_list(self, obj)

# 產生menu裡的action，之後若有新增的action增加在此method裡

```

```python
def action_trigger_connect(self, fn)

# menu裡action按下後要trig的connect method
```

```python
def setEnable(self, open)

# 此 method 可讓 action 初始為不可選取
```







