import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from myLib.myFilter import filter


class SF:

    def __init__(self):
        self.fog_raw_slow_x = None
        self.ixblue_setting_rate_slow = None
        self.fog_raw_slow = None
        self.ixblue_actual_rate_slow = None
        self.fog_raw = None
        self.ixblue_setting_rate = None
        self.ixblue_actual_rate = None
        self.kal = filter.kalman_1D()

    def load_data(self):
        filename = 'SP10_K_fast' + '.txt'
        filename2 = 'SP10_K_fast_ixblue' + '.txt'
        filename3 = 'SP10_K_slow' + '.txt'
        filename4 = 'SP10_K_slow_ixblue' + '.txt'

        data_fog = pd.read_csv(filename, comment='#', skiprows=0, chunksize=None)
        data_ixblue = pd.read_csv(filename2, comment='#', skiprows=0, chunksize=None, sep='\t')
        data_fog_slow = pd.read_csv(filename3, comment='#', skiprows=0, chunksize=None)
        # data_ixblue_slow = pd.read_csv(filename4, comment='#', skiprows=0, chunksize=None, sep='\t')
        key1 = data_ixblue.keys()[1]
        key2 = data_ixblue.keys()[2]
        self.ixblue_actual_rate = np.array(data_ixblue[key1])
        self.ixblue_setting_rate = np.array(data_ixblue[key2])
        self.fog_raw = np.array(data_fog['fog'])

        self.fog_raw_slow = np.array(data_fog_slow['fog'])
        self.fog_raw_slow_x, self.fog_raw_slow = self.filter_data(5000, self.fog_raw_slow[0:-1500])


        idx_ixblue_act = self.get_data_idx(self.ixblue_actual_rate, EN=False)
        avg_ixblue_act = self.get_avg(self.ixblue_actual_rate, idx_ixblue_act, EN=False)

        idx_ixblue_set = self.get_data_idx(self.ixblue_setting_rate)
        avg_ixblue_set = self.get_avg(self.ixblue_setting_rate, idx_ixblue_set)

        idx_fog_raw = self.get_data_idx(self.fog_raw, vth=14000, EN=False, pts=5)
        avg_fog_raw = self.get_avg(self.fog_raw, idx_fog_raw, EN=False)

        self.sf_fitting(avg_ixblue_act[0:14], avg_ixblue_set[0:14])
        # a, b = self.sf_fitting(avg_fog_raw[0:14], avg_ixblue_act[0:14])
        a = self.sf_fitting(avg_fog_raw[0:14], avg_ixblue_act[0:14])
        self.plot_result(a, 0, avg_ixblue_set[0:14], avg_ixblue_act[0:14], avg_fog_raw[0:14], self.fog_raw_slow)

    def filter_data(self, R, measure, pts=10):
        self.kal.kal_R = R
        data = np.empty(0)
        x = np.empty(0)
        ds_data = np.empty(0)  # down_sample_data
        size = int(len(measure) / 1)
        print('filter_data.len(measure): ', size)
        for i in range(0, size):
            if i % pts == 0:
                ds_data = np.append(ds_data, self.kal.update(measure[i]))
                x = np.append(x, i)
                data = np.append(data, self.kal.update(measure[i]))
        print('filter_data.len(ds_data): ', len(ds_data))
        plt.subplot(121)
        # plt.plot(measure, 'b')
        # plt.plot(x, data, 'r')
        # plt.subplot(122)
        # plt.plot(x, ds_data, 'k')
        # plt.show()
        return x, ds_data

    def plot_slow(self):
        pass

    def plot_result(self, a, b, x, ixblue, fog_raw, fog_slow_raw):
        deviation = np.empty(0)
        # sf_a = 1/a
        # print('sf_a: ', sf_a)
        fog = fog_raw * a + b
        fog_slow = (fog_slow_raw * a + b) * 3600
        rate_max = np.max(ixblue)
        print('rotation rate max [dps]: ', rate_max)
        for i in range(0, len(ixblue)):
            # print(i)
            deviation = np.append(deviation, ((fog[i] - ixblue[i]) / rate_max) * 1e6)
        # print(deviation)
        plt.subplot(221)
        # fig, ax1 = plt.subplots()
        # ax1.plot(x, ixblue, 'b*-', x, fog, 'ro')
        plt.plot(x, ixblue, 'b*-', x, fog, 'ro')
        plt.xlabel('rotation rate setting [dps]', fontsize=10)
        plt.ylabel('rotation rate [dps]', fontsize=10)
        plt.legend(['ixblue', 'fog'])
        plt.subplot(222)
        plt.plot(x, deviation, 'k*-')
        plt.xlabel('rotation rate setting [dps]', fontsize=10)
        plt.ylabel('non-linearity [ppm]', fontsize=10)
        plt.subplot(212)
        plt.plot(fog_slow)
        plt.ylabel('rotation rate [dph]', fontsize=10)
        plt.grid()
        plt.show()

    def get_data_idx_filter(self, data, x, vth=5.0, EN=False, pts=1):
        size = len(data)
        data_shift_one = np.array(data[pts:size])
        data = data[0:size - pts]
        diff_data = np.abs(data_shift_one - data)

        diff_data_bool = diff_data > vth
        idx = np.where(diff_data_bool)[0]
        idx_group = np.empty(0)

        for i in range(0, len(diff_data_bool) - 1):
            if (diff_data_bool[i]) and (not diff_data_bool[i + 1]):
                idx_group = np.append(idx_group, i)
        idx_group2 = np.split(idx_group, len(idx_group) / 2)
        if EN:
            print(size)
            # print(idx)
            print(idx_group)
            print(idx_group2)
            print(len(idx_group2))
        if EN:
            plt.subplot(121)
            plt.plot(data, '*-')
            plt.subplot(122)
            plt.plot(diff_data)
            plt.plot(idx_group, np.ones(len(idx_group)), '*-')
            plt.show()
        return idx_group2

    def get_data_idx(self, data, vth=5.0, EN=False, pts=1):
        size = len(data)
        data_shift_one = np.array(data[pts:size])
        data = data[0:size - pts]
        diff_data = np.abs(data_shift_one - data)

        diff_data_bool = diff_data > vth
        idx = np.where(diff_data_bool)[0]
        idx_group = np.empty(0)
        if EN:
            plt.subplot(121)
            plt.plot(data, '*-')
            plt.subplot(122)
            plt.plot(diff_data)
            plt.show()

        for i in range(0, len(diff_data_bool) - 1):
            if (diff_data_bool[i]) and (not diff_data_bool[i + 1]):
                idx_group = np.append(idx_group, i)
        idx_group2 = np.split(idx_group, len(idx_group) / 2)
        if EN:
            print(size)
            # print(idx)
            print(idx_group)
            print(idx_group2)
            print(len(idx_group2))
        # if EN:
            # plt.subplot(121)
            # plt.plot(data, '*-')
            # plt.subplot(122)
            # plt.plot(diff_data)
            # plt.plot(idx_group, np.ones(len(idx_group)), '*-')
            # plt.show()
        return idx_group2

    def get_avg(self, data, idx_group, EN=False):
        avg = np.empty(0)
        std = np.empty(0)

        for i in range(len(idx_group)):
            idx1 = int(idx_group[i][0]) + 10
            idx2 = int(idx_group[i][1]) - 10
            avg = np.append(avg, np.mean(data[idx1:idx2]))
            std = np.append(std, np.std(data[idx1:idx2]))

        if EN:
            plt.subplot(121)
            plt.plot(data)
            plt.subplot(122)
            plt.plot(avg, 'o-')
            plt.show()

        return avg

    def sf_fitting(self, x, y):

        par, _ = curve_fit(self.fit_linear2, x, y)
        # a, b = par
        a = par
        # print('y = %.10f * x + %.10f' % (a, b))
        print('y = %.10f * x' % a)
        return a

    def fit_linear(self, x, a, b):
        return a * x + b

    def fit_linear2(self, x, a):
        return a * x


if __name__ == '__main__':
    tt = SF()
    tt.load_data()
