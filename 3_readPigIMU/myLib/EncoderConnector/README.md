# EncoderConnector
本專案主要功能為透過socket與NI的伺服器連線，以TCP方式接收編碼器(Encoder)的狀態值。本專案可接收的編碼器之狀態值如下：
- 從NI伺服器上傳輸過來的資料之編號
- 編碼器位置
- 目前車輛移動距離
- 車輛之車速
- 車輛之車速的加速度

-------------------------------------
## 目錄
- [EncoderConnector](#encoderconnector)
  - [目錄](#目錄)
  - [檔案說明：](#檔案說明)
  - [使用說明](#使用說明)
    - [類別`myEncoderReader`](#類別myencoderreader)
    - [類別`myEncoderConnector`](#類別myencoderconnector)
  - [安裝](#安裝)
    - [使用`whl`檔安裝](#使用whl檔安裝)
    - [指定本專案連結給Python](#指定本專案連結給python)

-------------------------------------

## 檔案說明：
下表為本專案中目錄`EncoderConnector`中幾個重要檔案的用途：

檔名                   | 用途
---------------------|------------------------------------------------
`myEncoderConnector.py`    | 該檔案實作類別`myEncoderConnector`，功能為透過socket來接受編碼器的狀態值
`myEncoderReader.py`       | 該檔案實作類別`myEncoderReader`，功能為以執行緒的方式使用`myEncoderConnector.py`來取得編碼器的狀態值
`myEncoderGenerator.py`    | 該檔案實作了類別`myEncoderGenerator`，該類別會產生假資料並透過socket傳輸出去，主要功能為測試`myEncoderConnector.py`與`myEncoderConnector.py`

本專案目錄下有四個檔案用於測試與示範該如何使用本專案的程式：

檔名                   | 用途
---------------------|------------------------------------------------
`testEncoderGenerator_func.py`  | 該檔案示範了該如何使用類別`myEncoderGenerator`產生假資料，然後使用類別`myEncoderReader`來接受編碼器的狀態值
`testEncoderGenerator_object.py` | 功能與`testEncoderGenerator_func.py`相同，但是該檔案以物件導向的方式來示範如何使用類別`myEncoderReader`
`testEncoderReader_func.py`     | 該檔案示範了如何使用類別`myEncoderReader`來接受NI傳來的編碼器的狀態值
`testEncoderReader_object.py`   | 功能與`testEncoderReader_func.py`相同，但是該檔案以物件導向的方式來示範如何使用類別`myEncoderReader`
`testEncoderConnector.py`       | 該檔案示範了如何使用`myEncoderConnector`透過sockt與伺服器連線，來取得編碼器的狀態值。

## 使用說明
### 類別`myEncoderReader`
這邊來說明如何使用類別`myEncoderReader`，該類別會執行一個執行緒，在這個執行緒中會持續接受NI傳輸的編碼器的狀態值。使用方式如下：
1. 建立類別`myEncoderReader`的物件
    ```python
    from EncoderConnector import myEncoderReader

    oReader = myEncoderReader()
    ```
    下表為說明類別`myEncoderReader`之建構子可傳入的參數：
    參數名稱    | 型態      | 說明
    -----------|-----------|--------------------------------------------
    strIP      | str        | 用於指定伺服器的IP，預設是`192.168.1.178`
    iPort       | int       | 用於指定伺服器的Port，預設為`9000`
    fUpdateTime | float     | 用於控制輸出編碼器狀態的更新率，單位是秒，預設是`5ms`

2. 請先宣告一個帶有僅一個參數的函數作為Callback function，該函數的功能為提供給類別`myEncoderReader`之物件一個介面，來把接受到的編碼器之狀態值拿來使用：
    ```python
    def getStatus(dctStatus:dict):
        strSequence = dctStatus["Sequence"]
        iStep = dctStatus["Step"]
        fDistance = dctStatus["Distance"]
        fEncoderSpeed = dctStatus["EncoderSpeed"]
        fVehicleSpeed = dctStatus["VehicleSpeed"]
        fVehicleAcceleration = dctStatus["VehicleAcceleration"]

        """
        To do something
        """ 
        ...
    # End of getStatus
    ```
    這邊需要注意一點，類別`myEncoderReader`之物件會傳入一個`dict`的變數當作Callback function的參數，該參數的內容如下表：
    Key         | 型態      | 說明
    ------------|-----------|-------------------------
    Sequence    | str       | 代表收到第幾筆狀態值
    Step        | int       | 代表編碼器的位置
    Distance    | float     | 用以表示移動距離，單位是公尺(m)    
    EncoderSpeed| float     | 用以表示編碼器的速度，單位：$\frac{編碼器位置}{秒}$
    VehicleSpeed| float     | 用以表示當前的車速，單位是$\frac{Km}{Hr}$
    VehicleAcceleration| float | 用以表示當前車輛的加速度，單位是$\frac{Km}{{second}^2}$

3. 將Callback function指定給類別`myEncoderReader`使用：
    ```python
    oReader.setCallback(getStatus)
    ```

4. 呼叫成員函數`connectServer()`來與伺服器連線：
    ```python
    oReader.connectServer()
    ```

5. 請啟動類別`myEncoderReader`之物件，來接受編碼器的狀態值：
    ```python
    oReader.start()
    ```

6. 在確定不再使用類別`myEncoderReader`之物件，請關閉該類別的物件：
    ```python
    oReader.isRun = False
    oReader.join()
    ```

最後提醒一下，這邊的教學採用函數導向，所以這邊的Callback function也是一個函數，可參考範例程式`testEncoderReader_func.py`。然而，實際上Callback function也可以是類別中的方法，用法可以參考範例程式`testEncoderReader_object.py`。

### 類別`myEncoderConnector`
類別`myEncoderConnector`是類別`myEncoderReader`的底層實作，該類別才是實際與NI的伺服器溝通的介面。接下來說明該如何使用類別`myEncoderConnector`：
1. 建立類別`myEncoderConnector`之物件：
    ```python
    from EncoderConnector import myEncoderConnector

    oEncoderConnector = myEncoderConnector()
    ```
    下表為類別`myEncoderConnector`之建構子可傳入的參數：
    參數名稱    | 型態      | 說明
    -----------|-----------|--------------------------------------------
    strIP      | str        | 用於指定伺服器的IP，預設是`192.168.1.178`
    iPort       | int       | 用於指定伺服器的Port，預設為`9000`

2. 呼叫成員函數`connect()`來與伺服器連線
    ```python
    try:
        oEncoderConnector.connect()
    except Exception as oEx:
        print(oEx)
    # End of try-catch
    ```

3. 呼叫成員函數`obtainStatus()`來接受編碼器的狀態值
    ```python
    strSequence, iStep, fDistance, fEncoderSpeed, fVehicleSpeed, fVehicleAcceleration = oEncoderConnector.obtainStatus()
    ```
    下表列出成員函數`obtainStatus()`每個回傳值的狀態與功用：
    型態      | 說明
    -----------|-------------------------
    str       | 代表收到第幾筆狀態值
    int       | 代表編碼器的位置
    float     | 用以表示移動距離，單位是公尺(m)    
    float     | 用以表示編碼器的速度，單位：$\frac{編碼器位置}{秒}$
    float     | 用以表示當前的車速，單位是$\frac{Km}{Hr}$
    float | 用以表示當前車輛的加速度，單位是$\frac{Km}{{second}^2}$

4. 若不再使用，請關閉連線
    ```python
    oEncoderConnector.close()
    ```

如果想看完整的程式碼，可以參考本專案目錄下的`testEncoderConnector.py`。

## 安裝
### 使用`whl`檔安裝
請依以下的步驟來安裝本專案：
1. 使用下面的指令來產生`whl`檔：
    ```bash
    python setup.py bdist_wheel
    ```

2. `whl`檔將會存放於目錄`dist`中，請在終端機中切換目錄到`dist`，然後使用下面的指令來安裝：
    ```bash
    pip install EncoderConnector*.whl
    ```

### 指定本專案連結給Python
若在使用本專案來開發程式時，又希望測試本專案，可以使用這個方式來安裝。安裝方式為：
```bash
python setup.py develop
```

這個安裝方式和`whl`檔安裝最大的不同之處就在於，當更動本專案的程式碼時，前者什麼都不用做就可以使用到最新更動的程式碼，但是後者必須重新產生`whl`檔，並且透過該檔案來更新才行。