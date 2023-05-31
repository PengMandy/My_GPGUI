# common function

此 module 定義常用到的 methods

- [common function](#common-function)
  - [dictOperation](#dictoperation)
    - ["ADD"](#add)
    - ["SUB"](#sub)
    - ["APPEND"](#append)
  - [file_manager](#file_manager)
    - [使用](#使用)
  - [saveData2File](#savedata2file)
    - [使用](#使用-1)
  - [data_manager](#data_manager)
    - [使用](#使用-2)
  - [parameters_manager](#parameters_manager)
    - [使用](#使用-3)

## dictOperation

```python
def dictOperation(dictA: dict, dictB: dict, mode: str):

mode: str = "ADD" or "SUB" or "APPEND"

```

imudata dictionary 運算，imudata之結構為:

IMU_DATA_STRUCTURE =
{
    "NANO33_W": (wx, wy, wz),
    "NANO33_A": (ax, ay, az),
    "ADXL_A": (ax, ay, az),
    "TIME": (t,)
}

目前使用到的場景:

### "ADD"

1. 計算immudata offset值時會連續取data, 累加後取平均值

```python
#根據IMU_DATA_STRUCTURE宣告imuoffset之結構，讓個element為0
imuoffset = {k: np.zeros(len(IMU_DATA_STRUCTURE[k])) for k in set(IMU_DATA_STRUCTURE)}
print(imuoffset)
data = {
    "NANO33_W": (1, 2, 3),
    "NANO33_A": (-1, -2, -3),
    "ADXL_A": (4, 5, 6),
    "TIME": (1.5,)
}
for i in range(10):
    imuoffset = dictOperation(imuoffset, data, "ADD")
print(imuoffset)

imuoffset = {k: imuoffset[k]/10 for k in imuoffset}
print(imuoffset)

```

results:

```python
{'NANO33_W': array([0., 0., 0.]), 'NANO33_A': array([0., 0., 0.]), 'TIME': array([0.]), 'ADXL_A': array([0., 0., 0.])}
{'NANO33_W': array([10., 20., 30.]), 'NANO33_A': array([-10., -20., -30.]), 'TIME': array([15.]), 'ADXL_A': array([40., 50., 60.])}
{'NANO33_W': array([1., 2., 3.]), 'NANO33_A': array([-1., -2., -3.]), 'TIME': array([1.5]), 'ADXL_A': array([4., 5., 6.])}
```

2. 計算整體imudata加上一個offset值

```python
imudata = {
    "NANO33_W": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "NANO33_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "ADXL_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "TIME": (np.array([1.5, 1.6, 1.7]))
}
print(imudata)
offset = {
    "NANO33_W": (1, 2, 3),
    "NANO33_A": (-1, -2, -3),
    "ADXL_A": (4, 5, 6),
    "TIME": (1.5,)
}
imudata_add_offset = dictOperation(imudata, offset, "ADD")
print(imudata_add_offset)
```

results:

```python
{'NANO33_W': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'NANO33_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'ADXL_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'TIME': array([1.5, 1.6, 1.7])}
{'NANO33_W': array([[ 2,  3,  4],
                    [ 6,  7,  8],
                    [10, 11, 12]]), 
'NANO33_A': array([[0, 1, 2],
                   [2, 3, 4],
                   [4, 5, 6]]), 
'ADXL_A': array([[ 5,  6,  7],
                 [ 9, 10, 11],
                 [13, 14, 15]]), 
'TIME': array([3. , 3.1, 3.2])}
```

### "SUB"

計算整體imudata加上一個offset值

```python
imudata = {
    "NANO33_W": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "NANO33_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "ADXL_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
    "TIME": (np.array([1.5, 1.6, 1.7]))
}
print(imudata)
offset = {
    "NANO33_W": (1, 2, 3),
    "NANO33_A": (-1, -2, -3),
    "ADXL_A": (4, 5, 6),
    "TIME": (1.5,)
}
imudata_add_offset = dictOperation(imudata, offset, "SUB")
print(imudata_add_offset)
```

results:

```python
{'NANO33_W': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'NANO33_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'ADXL_A': (array([1, 2, 3]), array([4, 5, 6]), array([7, 8, 9])), 'TIME': array([1.5, 1.6, 1.7])}
{'NANO33_W': array([[0, 1, 2],
                    [2, 3, 4],
                    [4, 5, 6]]), 
'NANO33_A': array([[ 2,  3,  4],
                   [ 6,  7,  8],
                   [10, 11, 12]]), 
'ADXL_A': array([[-3, -2, -1],
                 [-1,  0,  1],
                 [ 1,  2,  3]]), 
'TIME': array([0. , 0.1, 0.2])}
```

### "APPEND"

1. 在memsImuReader裡對每個imudata append

```python
imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
                    for k in set(IMU_DATA_STRUCTURE)}
imudata = {
    "NANO33_W": np.array((1., 2., 3.)),
    "NANO33_A": np.array((-1., -2., -3.)),
    "ADXL_A": np.array((4., 5., 6.)),
    "TIME": (1.5,)
}
print(imudataArray)
for i in range(5):
    imudataArray = dictOperation(imudataArray, imudata, "APPEND")
print(imudataArray)
```

results:

```python
{'NANO33_W': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'ADXL_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'NANO33_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'TIME': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)]}
{'NANO33_W': [array([1., 1., 1., 1., 1.]), array([2., 2., 2., 2., 2.]), array([3., 3., 3., 3., 3.])], 'ADXL_A': [array([4., 4., 4., 4., 4.]), array([5., 5., 5., 5., 5.]), array([6., 6., 6., 6., 6.])], 'NANO33_A': [array([-1., -1., -1., -1., -1.]), array([-2., -2., -2., -2., -2.]), array([-3., -3., -3., -3., -3.])], 'TIME': array([1.5, 1.5, 1.5, 1.5, 1.5])}

```

2. 測試在main裡 對memsImuReader發送來的imudata append
   
```python
data1 = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
                for k in set(IMU_DATA_STRUCTURE)}
data2 = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
            for k in set(IMU_DATA_STRUCTURE)}
imudata = {
    "NANO33_W": np.array((1., 2., 3.)),
    "NANO33_A": np.array((-1., -2., -3.)),
    "ADXL_A": np.array((4., 5., 6.)),
    "TIME": (1.5,)
}

for i in range(5):
    data1 = dictOperation(data1, imudata, "APPEND")

print(data1)
print(data2)
data1["TIME"] = [data1["TIME"]]
for i in range(3):
    data2 = dictOperation(data2, data1, "APPEND")
print(data2)
```

```python
{'TIME': array([1.5, 1.5, 1.5, 1.5, 1.5]), 'NANO33_A': [array([-1., -1., -1., -1., -1.]), array([-2., -2., -2., -2., -2.]), array([-3., -3., -3., -3., -3.])], 'NANO33_W': [array([1., 1., 1., 1., 1.]), array([2., 2., 2., 2., 2.]), array([3., 3., 3., 3., 3.])], 'ADXL_A': [array([4., 4., 4., 4., 4.]), array([5., 5., 5., 5., 5.]), array([6., 6., 6., 6., 6.])]}
{'TIME': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'NANO33_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'NANO33_W': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)], 'ADXL_A': [array([], dtype=float64), array([], dtype=float64), array([], dtype=float64), array([], dtype=float64)]}
{'TIME': array([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
       1.5, 1.5]), 'NANO33_A': [array([-1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,
       -1., -1.]), array([-2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2., -2.,
       -2., -2.]), array([-3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3., -3.,
       -3., -3.])], 'NANO33_W': [array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]), array([2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2., 2.]), array([3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3.])], 'ADXL_A': [array([4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4.]), array([5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5.]), array([6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6., 6.])]}

```

## file_manager

此method用來管理要新增與關上的檔案，定義:
```python
def file_manager(isopen=False, name="notitle", mode="w", fnum=0):

isopen = True: 開啟檔案
isopen = False: 關上已開啟的檔案 or 不做任何事

return bool, fd

bool: 若開啟檔案成功回傳True，否則False
fd: 若開啟檔案成功回傳obj，否則None

```
### 使用

在要打開檔案處與結束處放入 (此處為main裡按下read button 與 stop button處)

```python
def start(self):
    self.act.readIMU()
    self.act.isRun = True
    self.act.start()
    # 跟file_manager要一個空間，並開啟"imu1.txt"檔案，若成功則isFileOpen為True，
    #File_fd為檔案描述符
    self.isFileOpen, self.File_fd= cmn.file_manager(self.top.save_rb.isChecked(), "imu1.txt")


def stop(self):
    self.act.isRun = False
    self.top.save_rb.setChecked(False)
    #當引述isopen為False時，若有先開啟了檔案，則file_manager會根據fnum引數來關閉檔案，
    #此處無fnum代表預設為第0個檔案; 若無先開啟檔案，則什麼事也不做。
    self.isFileOpen, self.File_fd= cmn.file_manager(self.top.save_rb.isChecked(), "imu1.txt")
```

若在執行的py裡只使用到一個存取檔案，則funm不需填入，預設為0。若超過一個則需加上對應編號，注意開與關需成對出現，其中open_status: bool 需由使用者控制輸出，開檔: True, 關檔: False
目前設定同一個py只能開啟兩個檔案，若益擴增需至common.py裡將fd 之 None list擴增

```python
fd = [None, None]
```

```python
def start1:
    self.isFileOpen1, self.File_fd1= cmn.file_manager(open_status1, "imu1.txt", 0)

def start2:
    self.isFileOpen2, self.File_fd2= cmn.file_manager(open_status2, "imu2.txt", 1)

def stop1:
    self.isFileOpen1, self.File_fd1= cmn.file_manager(open_status1, "imu1.txt", 0)

def stop2:
    self.isFileOpen2, self.File_fd2= cmn.file_controller(open_status2, "imu2.txt", 1)

```

## saveData2File

此 mathod搭配file_manager使用，將file_manager 回傳之 isopen 與 fd 丟入，再將欲寫入的 data 與 fomat丟入即可。 注意 data 形式為 list: 
eg. data = [data1, data2, data3........]，其中data(n) 可為array

```python
def saveData2File(isopen: bool = False, data: list = None, fmt: str = " ", file: object = None):
```

### 使用
```python
data = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["NANO33_WZ"]
            , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]]

data_fmt = "%.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f"

cmn.saveData2File(self.__isFileImuOpen, data, data_fmt, self.__FileImu_fd)
```

## data_manager

此 class 用來管理儲存數據檔案，定義:

```python
def __init__(self, name="untitled.txt", fnum=0):
    self.__fd = None
    self.__isopen = False
    self.__name__ = name
    self.__fnum__ = fnum

name: 參數檔案名稱
funm : file_manager 之 fnum 引數
```

類別提供之公用 method:

```python
@name.setter
def name(self, name)

可讓使用者在宣告類別物件以後再決定名稱
```

```python
def open(self, status)

若 status = True 時則依照 name 來產生檔案，並且在首行寫入日期
```

```python
def close(self)

關掉名稱為 name 的檔案，並且在末行寫入日期
```

```python
def saveData(self, datalist, fmt)

同等於 saveData2File()
```

### 使用

```python
#宣告類別物件
def __init__(self):
self.imudata_file = cmn.data_manager(fnum=0)

# 在檔案開始寫之前打開檔案，status 與 name 由 gui 按鈕來控制
def start(self):
    file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
    self.imudata_file.name = file_name
    self.imudata_file.open(self.top.save_block.rb.isChecked())

# 在檔案結束時關掉檔案
def stop(self):
    self.imudata_file.close()

# 在主程式運行中將datalist寫入檔案
def collectData(self):
    datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["NANO33_WZ"]
            , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]]
        data_fmt = "%.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f"
        self.imudata_file.saveData(datalist, data_fmt)

```

## parameters_manager

此 class 用來管理fog參數，其定義為:

```python
def __init__(self, name, parameter_init, fnum=1):
    self.__par = parameter_init
    self.__name = name
    self.__fnum = fnum

name: 參數檔案名稱
parameter_init: 參數初始值dictionary
funm : file_manager 之 fnum 引數
```

類別提供之公用 method:

```python
def check_file_exist(self) -> dict:

若要先確認使否存在既有參數檔案，需在開始處將此方法放置在 update_parameters 前，
藉由 file_manager 回傳之 fd.mode 判斷是否有既有參數檔案，若無則依照 name 生成
新檔案並將 parameter_init 內容寫入，同時回傳內容為 parameter_init 的 dict; 
若已有參數檔案，則將其讀入並回傳。
```


```python
def update_parameters(self, key, value):

將參數新的值寫入參數檔案裡，key 需與參數檔案裡定義的相同。

```

### 使用

```python

INIT_PARAMETERS = {"MOD_H": 3250,
                   "MOD_L": -3250,
                   "FREQ": 139,
                   "DAC_GAIN": 290,
                   "ERR_OFFSET": 0,
                   "POLARITY": 1,
                   "WAIT_CNT": 65,
                   "ERR_TH": 0,
                   "ERR_AVG": 6,
                   "GAIN1": 6,
                   "GAIN2": 5,
                   "FB_ON": 1,
                   "CONST_STEP": 0,
                   "KF_Q": 1,
                   "KF_R": 6,
                   "SF_A": 0.00295210451588764 * 1.02 / 2,
                   "SF_B": -0.00137052112589694,
                   "DATA_RATE": 1863
                   }

class pig_parameters_widget(QGroupBox):
    def __init__(self, act):
        super(pig_parameters_widget, self).__init__()
        print("import pigParameters")
        self.__act = act
        # 產生 parameters_manager 物件，給定檔案名稱與初始參數 dict
        self.__par_manager = cmn.parameters_manager("parameters_SP9.json", INIT_PARAMETERS, 1)
        .
        .
        .
        self.initUI()
        # 檢查檔案是否存在
        initPara = self.__par_manager.check_file_exist()
        self.set_init_value(initPara)
        self.linkfunction()


    def send_FREQ_CMD(self):
        value = self.freq.spin.value()
        print('set freq: ', value)
        self.freq.lb.setText(str(round(1 / (2 * (value + 1) * 10e-6), 2)) + ' KHz')
        self.__act.writeImuCmd(CMD_FOG_MOD_FREQ, value)
        # 參數更新後加入此行來更新檔案裡對應的參數
        self.__par_manager.update_parameters("FREQ", value)

```

