# 使用QTheard

- [使用QTheard](#使用qtheard)
  - [定義一個class, 繼承QObject, 在class內connect signal](#定義一個class-繼承qobject-在class內connect-signal)
  - [定義一個class, 繼承QThread, 在class內connect](#定義一個class-繼承qthread-在class內connect)
  - [使用QThread方式因為需要執行class.start()後才會執行迴圈部分，因此可直接可在class外connect](#使用qthread方式因為需要執行classstart後才會執行迴圈部分因此可直接可在class外connect)

## 定義一個class, 繼承QObject, 在class內connect signal
若不是繼承QObject而是QWidget，執行時要改成:
```python
app = QApplication(sys.argv)
tt = TestSignal()
app.exec_()
```

```python
class TestSignal(QObject):
    update = pyqtSignal(int)

    def __init__(self):
        super(TestSignal, self).__init__()
        self.cnt=0
        self.update.connect(self.getPyqtsignal)
        self.update.connect(getPyqtsignal)
        self.fn()

    def fn(self):
        while self.cnt<10:
            self.cnt += 1
            self.update.emit(self.cnt)
            time.sleep(0.5)

    def getPyqtsignal(self, data):
        print("in getPyqtsignal:", data)

def getPyqtsignal(data):
    print("out getPyqtsignal:", data)

if __name__ == "__main__":
    tt = TestSignal()

```

```commandline
result:
in getPyqtsignal: 1
out getPyqtsignal: 1
in getPyqtsignal: 2
out getPyqtsignal: 2
in getPyqtsignal: 3
out getPyqtsignal: 3
in getPyqtsignal: 4
out getPyqtsignal: 4
```

注意若不是在內部connect而是在外部的話，*需要先connect後再執行迴圈*，不然會收不到 update.emit
```python
class TestSignal(QWidget):
    update = pyqtSignal(int)

    def __init__(self):
        super(TestSignal, self).__init__()
        self.cnt=0
        # self.update.connect(self.getPyqtsignal)
        # self.update.connect(getPyqtsignal)
        # self.fn()

    def fn(self):
        while self.cnt<10:
            self.cnt += 1
            self.update.emit(self.cnt)
            time.sleep(0.5)

    def getPyqtsignal(self, data):
        print("in getPyqtsignal:", data)

def getPyqtsignal(data):
    print("out getPyqtsignal:", data)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tt = TestSignal()
    '''-----connect first------'''
    tt.update.connect(tt.getPyqtsignal)
    tt.update.connect(getPyqtsignal)
    '''-----do loop later------'''
    tt.fn()
    app.exec_()
```


## 定義一個class, 繼承QThread, 在class內connect

```python
class TestThread(QThread):
    update = pyqtSignal(int)

    def __init__(self):
        super(TestThread, self).__init__()
        self.update.connect(self.getPyqtsignal)
        self.update.connect(getPyqtsignal)
        self.cnt = 0

    def run(self):
        while self.cnt < 100:
            self.cnt += 1
            self.update.emit(self.cnt)
            time.sleep(0.5)

    def getPyqtsignal(self, data):
        print("in getPyqtsignal:", data)


def getPyqtsignal(data):
    print("out getPyqtsignal:", data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tt = TestThread()
    tt.start()
    app.exec_()
```

## 使用QThread方式因為需要執行class.start()後才會執行迴圈部分，因此可直接可在class外connect

```python
class TestThread(QThread):
    update = pyqtSignal(int)

    def __init__(self):
        super(TestThread, self).__init__()
        # self.update.connect(self.getPyqtsignal)
        # self.update.connect(getPyqtsignal)
        self.cnt = 0

    def run(self):
        while self.cnt < 100:
            self.cnt += 1
            self.update.emit(self.cnt)
            time.sleep(0.5)

    def getPyqtsignal(self, data):
        print("in getPyqtsignal:", data)


def getPyqtsignal(data):
    print("out getPyqtsignal:", data)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    tt = TestThread()
    tt.start()
    tt.update.connect(tt.getPyqtsignal)
    tt.update.connect(getPyqtsignal)
    app.exec_()
```