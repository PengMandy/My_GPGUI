import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import os, sys

file = 'freq.csv'
# row_len = 20
Var1 = pd.read_csv(file, comment='#', skiprows=0, chunksize=None)
print(Var1)
# Var2 = pd.read_csv('0725-2.txt', comment='#', skiprows=0, chunksize=None)
# t1 = Var1['time'][37000:-1]
# t2 = Var2['time']
# w1 = Var1['fog'][37000:-1]
# w2 = Var2['fog']
# plt.figure(0)
# plt.plot(t1, w1, 'b-', t2, w2, 'r-')
# plt.ylabel('dps')
# plt.xlabel('s')
# plt.legend(['10F', '1F'])
# plt.show()

