import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


filename1 = '0923-3.txt'
filename2 = '0923.txt'

Var1 = pd.read_csv(filename1, comment='#', skiprows=0, chunksize=None)
# Var2 = pd.read_csv(filename2, comment='#', skiprows=0, chunksize=None)
time1 = np.array(Var1['time'][9:-1])
# time2 = np.array(Var2['time'][9:-1])
size1 = len(time1)
# size2 = len(time2)

# time1 = np.array(Var1['time'][9:size2+9])
# size1 = len(time1)

# print(size1, size2)

# accu = np.empty(0)
cnt = np.empty(0)

increment1 = time1 - time1[0]
# increment2 = time2 - time2[0]

for i in range(size1):
    cnt = np.append(cnt, i*0.01)
# accu = np.cumsum(cnt)

diff1 = cnt - increment1
# diff2 = cnt - increment2
plt.plot(diff1*1e3)
# plt.plot(diff2*1e3)

plt.xlabel('number', fontsize=10)
plt.ylabel('time diff [ms]', fontsize=10)
# plt.legend(['ext trigger', 'delay'])
plt.legend(['ext trigger'])
plt.show()
