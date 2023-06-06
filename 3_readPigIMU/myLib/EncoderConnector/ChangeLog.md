# Change Log

----------------------------------------
## [Unrelease]
### Added

### Changed

### Fixed

### Deprecated

### Removed

### Security

----------------------------------------
## [1.0.0] - 2022/03/09
### Added
- 新增模組`EncoderConnector`。
- 實作類別`myEncoderConnector`的建構子。
- 在類別`myEncoderConnector`中實作成員函數`connect()`和`close()`來處理連線。
- 在類別`myEncoderConnector`中實作成員函數`obtainStatus()`從伺服器接受編碼器的訊息。
- 新增類別`myEncoderReader`，該類別會以一個獨立的執行緒透過類別`myEncoderConnector`取得編碼器的訊息。
- 在類別`myEncoderReader`中實作成員函數`connectServer()`來連上伺服器。
- 在類別`myEncoderReader`中新增屬性`m_isRun`和setter和getter，該屬性用於控制該類別使否持續從伺服器獲取編碼器的訊息。
- 在類別`myEncoderReader`中實作成員函數`run()`，來提供可以長時間從伺服器中索取編碼器訊息的功能。
- 修改類別`myEncoderReader`，透過callback function來傳遞編碼器的訊息。
- 新增類別`myEncoderGenerator`，該類別主要用於產生假資料來測試本專案。
- 在類別`myEncoderGenerator`中新增屬性`m_isRun`，用以控制該類別是否持續產生假資料。
- 實作類別`myEncoderGenerator`傳送假資料到Client端的功能。
- 新增`testEncoderGenerator.py`來測試類別`myEncoderGenerator`和`myEncoderReader`。
- 新增`testEncoderReader.py`來測試類別`myEncoderReader`。
- 在類別`myEncoderReader`中新增成員函數`setCallback()`，來指定欲使用的Callback function。
- 新增`testEncoderConnector.py`來測試類別`myEncoderConnector`。

### Changed
- 原本測試類別`myEncoderGenerator`的測試程式碼移除掉，改用`testEncoderGenerator_func.py`和`testEncoderGenerator_object.py`，這兩者的差異在於前者以函數導向來實作Callback function，後者則使用物件導向。
- 原本只測試類別`myEncoderReader`的測試程式碼移除掉，改用`testEncoderReader_funct.py`和`testEncoderReader_object.py`，前者以函數導向來實作Callback function，後者則使用物件導向。

### Fixed
- 修正`testEncoderGenerator_func.py`的錯誤，這個錯誤是因為類別`myEncoderReader`設定Callback function的方式已經更改了，但測試程式沒有跟著修改。
- 修正`testEncoderReader_func.py`與`testEncoderReader_object.py`因沒呼叫類別`myEncoderReader`之成員函數`connectServer()`，而導致無法與伺服器連線。
- 修正類別`myEncoderConnector`之成員函數`obtainStatus()`在從伺服器接受資料時，因伺服器傳輸資料過快，導致Buffer中會儲存多筆資料，目前的解決辦法是使用`\r`這個符號去切割多筆資料，並只使用切割後的第一筆資料。
- 在類別`myEncoderConnector`中新增成員函數`receiveData()`來解決伺服器傳輸資料過快，而導致接收端來不及處理。
- 修正`testEncoderGenerator_func.py`沒顯示接收的訊息，原因是類別`myEncoderReader`之物件沒設定Callback function。

### Removed
- 移除從類別`myEncoderReader`中getter函數`isReceive()`。