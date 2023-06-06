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

import sys
import os

sys.path.append("../../")
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

filename = '20220712_sp9_SF' + '.txt'
filename2 = '20220712_ix_sp9_SF' + '.txt'

data = pd.read_csv(filename, comment='#', skiprows=0, chunksize=None)
data2 = pd.read_csv(filename2, comment='#', skiprows=0, chunksize=None, sep='\t')
t = data['time']
fog = data['fog']
t2 = data2['Time']
wa = np.array(data2['wa'])
wt = np.array(data2['wt'])
# plt.figure(0)
# plt.plot(wa)
# plt.plot(wt)
# plt.plot(fog)
size = len(wa)
print('len(wa): ', len(wa))
print('len(fog): ', len(fog))
wa2 = np.array(wa[1:size])
wa = wa[0:size - 1]
wt2 = np.array(wt[1:size])
wt = wt[0:size - 1]
fog2 = np.array(fog[1:len(fog)])
fog = fog[0:len(fog) - 1]
print('len(wa2): ', len(wa2))
diff_wa = np.abs(wa2 - wa)
# plt.figure(3)
# plt.plot(diff_wa)
# plt.show()

diff_wa2 = np.abs(wa2 - wa) > 5
idx1 = np.where(diff_wa2)[0]
idx_group = np.empty(0)

# breakpoint()

diff_wt = np.abs(wt2 - wt)
diff_wt2 = np.abs(wt2 - wt) > 5
idx2 = np.where(diff_wt2)[0]
idx2_group = np.empty(0)

diff_fog = np.abs(fog2 - fog)
# plt.figure(3)
# plt.plot(diff_fog)
diff_fog2 = np.abs(fog2 - fog) > 23000
idxfog = np.where(diff_fog2)[0]
idxfog_group = np.empty(0)
for i in range(0, len(diff_wa2) - 1):
    if (not diff_wa2[i]) and (diff_wa2[i + 1]):
        idx_group = np.append(idx_group, i)

for i in range(0, len(diff_wt2) - 1):
    if (not diff_wt2[i]) and (diff_wt2[i + 1]):
        idx2_group = np.append(idx2_group, i)

for i in range(0, len(diff_fog2) - 1):
    if (not diff_fog2[i]) and (diff_fog2[i + 1]):
        idxfog_group = np.append(idxfog_group, i)

idx_group2 = np.split(idx_group, len(idx_group)/2)
wa_avg = np.empty(0)
wa_std = np.empty(0)

idx2_group2 = np.split(idx2_group, len(idx2_group)/2)
wt_avg = np.empty(0)
wt_std = np.empty(0)

idxfog_group2 = np.split(idxfog_group, len(idxfog_group)/2)
fog_avg = np.empty(0)
fog_std = np.empty(0)

for i in range(len(idx_group2)):
    id1 = int(idx_group2[i][0]) + 10
    id2 = int(idx_group2[i][1]) - 10
    wa_avg = np.append(wa_avg, np.mean(wa[id1:id2]))
    wa_std = np.append(wa_std, np.std(wa[id1:id2]))

for i in range(len(idx2_group2)):
    id1 = int(idx2_group2[i][0]) + 10
    id2 = int(idx2_group2[i][1]) - 10
    wt_avg = np.append(wt_avg, np.mean(wt[id1:id2]))
    wt_std = np.append(wt_std, np.std(wt[id1:id2]))

for i in range(len(idxfog_group2)):
    id1 = int(idxfog_group2[i][0]) + 100
    id2 = int(idxfog_group2[i][1]) - 100
    # print(id1, id2)
    fog_avg = np.append(fog_avg, np.mean(fog[id1:id2]))
    fog_std = np.append(fog_std, np.std(fog[id1:id2]))

print(len(wa_avg), len(wa_std))
# print(wa_avg)
# print(wa_std)
print(len(wt_avg), len(wt_std))
print(len(fog_avg), len(fog_std))
# print(wt_avg)
# print(wt_std)
# plt.figure(1)
# plt.subplot(1,3,1)
# plt.plot(wt_avg)
# plt.subplot(1,3,2)
# plt.plot(fog_avg)
# plt.subplot(1,3,3)
sf = wt_avg/fog_avg
sf2 = wt_avg / wa_avg
# print('sf2: ', sf2)
# plt.plot(sf)
# plt.figure(2)
# plt.plot(fog_std)
# print(wt_avg)
sff = sf[0:14]
sff2 = sf2[0:14]

max_sf = np.max(sf)
min_sf = np.min(sf)
max_sf2 = np.max(sf2)
min_sf2 = np.min(sf2)
print('sf: ', min_sf, max_sf)
print('sf2: ', min_sf2, max_sf2)
plt.figure(4)
plt.subplot(121)
x = wt_avg[0:14]
wtt = wt_avg[0:14]
waa = wa_avg[0:14]
fog_avg_max = (fog_avg*max_sf)[0:14]
fog_avg_min = (fog_avg*min_sf)[0:14]
wa_avg_max = (wa_avg*max_sf2)[0:14]
wa_avg_min = (wa_avg*min_sf2)[0:14]
plt.plot(x, wtt, 'k-o')
plt.plot(x, fog_avg_max, 'r-o')
plt.plot(x, fog_avg_min, 'b-o')
plt.subplot(122)
err_fog_min = fog_avg_min - wtt
err_fog_max = fog_avg_max - wtt
ppm_fog_min = np.empty(0)
ppm_fog_max = np.empty(0)
ppm_wa_min = np.empty(0)
ppm_wa_max = np.empty(0)
for i in range(0, len(x)):
    # print(i, fog_avg_min[i], wtt[i])
    ppm_fog_min = np.append(ppm_fog_min, (fog_avg_min[i] - wtt[i]) / wtt[i] * 1e6)
    ppm_fog_max = np.append(ppm_fog_max, (fog_avg_max[i] - wtt[i]) / wtt[i] * 1e6)
    ppm_wa_min = np.append(ppm_wa_min, (wa_avg_min[i] - wtt[i]) / wtt[i] * 1e6)
    ppm_wa_max = np.append(ppm_wa_max, (wa_avg_max[i] - wtt[i]) / wtt[i] * 1e6)
# plt.plot(x, err_fog_min, 'b-*')
# plt.plot(x, err_fog_max, 'r-*')
plt.plot(x, ppm_fog_min, 'b-*')
plt.plot(x, ppm_fog_max, 'r-*')

plt.figure(0)
plt.subplot(121)
# plt.plot(x, sff)
plt.plot(x, wtt, 'k-o')
plt.plot(x, wa_avg_max, 'r-o')
plt.plot(x, wa_avg_min, 'b-o')
plt.subplot(122)
# plt.plot(x, sff2)
plt.plot(x, ppm_wa_min, 'b-*')
plt.plot(x, ppm_wa_max, 'r-*')

plt.show()
