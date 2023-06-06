import pandas as pd

Var = pd.read_csv(self.filename, comment='#', skiprows=0, chunksize=None)


def readData_fast(self):
    print('read_fast begin: ')
    t1 = time.perf_counter()
    # Var = pd.read_csv(self.filename, comment='#')
    # Var = pd.read_csv(self.filename, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0,
    #                   chunksize=None)
    Var = pd.read_csv(self.filename, comment='#', skiprows=0, chunksize=None)
    t2 = time.perf_counter()
    self.data_qt.emit(Var)
    # print(Var)
    print('read done: ', t2 - t1)