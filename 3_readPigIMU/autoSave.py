import sys
from datetime import datetime
import time
from os.path import exists
import os

sys.path.append("../../")
from myLib import common as cmn


class atSave_PC:

    def __init__(self, fnum=0):
        # self.__name = None
        self.__data_manager = cmn.data_manager(fnum=fnum)
        self.hh_path = None
        # self.data_path = rootPath + '/' + 'data'
        self.__data_path = None
        self.dd_path = None
        self.mm_path = None
        self.yy_path = None
        # self.__is_empty_folder = True
        self.start = True
        # self.__start = True

    def create_data_folder(self, en=False):
        if en:
            print('data path: ', self.data_path)
            file_exist = exists(self.data_path)
            print('data folder exist? : ', file_exist)
            if not file_exist:
                # self.__is_empty_folder = True
                os.mkdir(self.data_path, mode=0o777)
                print('     create data folder done.')

    def create_year_folder(self):
        yy = datetime.now().year
        self.yy_path = self.data_path + '/' + str(yy)
        file_exist = exists(self.yy_path)
        # print('year folder %s exist?: %s' % (self.yy_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.yy_path, mode=0o777)
            print('     create year folder %d done.' % yy)

    def create_month_folder(self):
        mm = datetime.now().month
        self.mm_path = self.yy_path + '/' + str(mm)
        file_exist = exists(self.mm_path)
        # print('month folder %s exist?: %s' % (self.mm_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.mm_path, mode=0o777)
            print('     create month folder %d done.' % mm)

    def create_day_folder(self):
        dd = datetime.now().day
        self.dd_path = self.mm_path + '/' + str(dd)
        file_exist = exists(self.dd_path)
        # print('day folder %s exist?: %s' % (self.dd_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.dd_path, mode=0o777)
            print('     create day folder %d done.' % dd)

    def auto_create_folder(self, en=False):
        if en:
            self.create_year_folder()
            self.create_month_folder()
            self.create_day_folder()
            self.open_hour_file()

    def open_hour_file(self):
        hh = datetime.now().hour
        self.hh_path = self.dd_path + '/' + str(hh) + '.txt'
        file_exist = exists(self.hh_path)
        # print('hour file %d.txt exist?: %s' % (hh, file_exist))
        if file_exist:
            if self.start:
                os.remove(self.hh_path)
                print('     remove hour file %d.txt done.' % hh)
                self.__data_manager.name = self.hh_path
                self.__data_manager.open(True)
                self.start = False
                print('     re-create hour file %d done.' % hh)

        else:
            if self.start:
                self.start = False
            else:
                self.close_hour_folder()
                print('     close hour file %d done.' % (hh - 1))
            self.__data_manager.name = self.hh_path
            self.__data_manager.open(True)
            print('     create hour file %d done.' % hh)

    def close_hour_folder(self):
        self.__data_manager.close()
        pass

    def write_line(self, comment):
        self.__data_manager.write_line(comment)

    def saveData(self, datalist, fmt):
        self.__data_manager.saveData(datalist, fmt)

    @property
    def data_path(self):
        return self.__data_path + '/' + 'data'

    @data_path.setter
    def data_path(self, path):
        self.__data_path = path

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, val):
        self.__start = val


class atSave_PC_v2:

    def __init__(self, fnum=0):
        # self.__name = None
        self.hh_reg = None
        self.hh = None
        self.dd = None
        self.mm = None
        self.yy = None
        self.__data_manager = cmn.data_manager(fnum=fnum)
        self.hh_path = None
        # self.data_path = rootPath + '/' + 'data'
        self.__data_path = None
        self.dd_path = None
        self.mm_path = None
        self.yy_path = None
        # self.__is_empty_folder = True
        self.start = True
        self.reset_hh_reg()
        # self.__start = True

    def reset_hh_reg(self):
        self.hh_reg = 99
        self.start = True

    def create_data_folder(self, en=False):
        if en:
            print('data path: ', self.data_path)
            file_exist = exists(self.data_path)  # 判斷資料夾是否存在
            print('data folder exist? : ', file_exist)
            if not file_exist:   # 如果資料夾不存在 (為true)
                # self.__is_empty_folder = True
                os.mkdir(self.data_path, mode=0o777)  # 僅限以數字模式建立資料夾(資料夾只能以數字命名)
                print('     create data folder done.')

    def create_year_folder(self):
        self.yy = datetime.now().year  # 年的數值
        self.yy_path = self.data_path + '/' + str(self.yy)
        file_exist = exists(self.yy_path)
        # print('year folder %s exist?: %s' % (self.yy_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.yy_path, mode=0o777)
            print('     create year folder %d done.' % self.yy)

    def create_month_folder(self):
        self.mm = datetime.now().month
        self.mm_path = self.yy_path + '/' + str(self.mm)
        file_exist = exists(self.mm_path)
        # print('month folder %s exist?: %s' % (self.mm_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.mm_path, mode=0o777)
            print('     create month folder %d done.' % self.mm)

    def create_day_folder(self):
        self.dd = datetime.now().day
        self.dd_path = self.mm_path + '/' + str(self.dd)
        file_exist = exists(self.dd_path)
        # print('day folder %s exist?: %s' % (self.dd_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.dd_path, mode=0o777)
            print('     create day folder %d done.' % self.dd)

    def auto_create_folder(self, en=False):
        if en:
            self.create_year_folder()
            self.create_month_folder()
            self.create_day_folder()
            self.open_hour_file()

    def open_hour_file(self):
        data = datetime.now()
        self.hh = data.hour
        MM = data.minute
        ss = data.second
        # file_name = self.dd_path + '/' + str(self.hh).zfill(2) + str(MM).zfill(2) + str(ss).zfill(2)
        file_name = self.dd_path + '/' + str(self.yy) + str(self.mm).zfill(2) + str(self.dd).zfill(2) + '_' + \
                    str(self.hh).zfill(2) + str(MM).zfill(2) + str(ss).zfill(2)     # zfill為在該字串的左邊添加0
        file_exist = (self.hh == self.hh_reg)
        if not file_exist:
            if self.start:
                self.start = False
            else:
                self.close_hour_folder()
            self.hh_path = file_name + '.txt'
            self.__data_manager.name = self.hh_path
            self.__data_manager.open(True)
            self.write_line('time,wx,wy,wz,ax,ay,az,yy,MM,dd,hh,mm,ss,ms')
            print('     create hour file %s done.' % self.__data_manager.name)
        self.hh_reg = self.hh

    def close_hour_folder(self):
        self.__data_manager.close()
        print('     close hour file %s done.' % self.__data_manager.name)
        pass

    def write_line(self, comment):   # 呼叫寫進txt檔案的method
        self.__data_manager.write_line(comment)

    def saveData(self, datalist, fmt):
        self.__data_manager.saveData(datalist, fmt)

    @property
    def data_path(self):
        return self.__data_path + '/' + 'data'

    @data_path.setter
    def data_path(self, path):
        self.__data_path = path

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, val):
        self.__start = val



class atSave_PC_v3:

    def __init__(self, fnum=0):
        # self.__name = None
        self.hh_reg = None
        self.hh = None
        self.dd = None
        self.mm = None
        self.yy = None
        self.__data_manager = cmn.data_manager(fnum=fnum)
        self.hh_path = None
        # self.data_path = rootPath + '/' + 'data'
        self.__data_path = None
        self.dd_path = None
        self.mm_path = None
        self.yy_path = None
        # self.__is_empty_folder = True
        self.start = True
        self.reset_hh_reg()
        # self.__start = True

    def reset_hh_reg(self):
        self.hh_reg = 99
        self.start = True

    def judgment_hh(self, en=False):  # 0605 修改流程判斷
        # 判斷小時值是否等於以記錄的小時值
        # 如果等於代表已經有資料夾被建立的
        # 如果不等於代表可能資料夾沒被建立
        now_hh = datetime.now().hour
        if self.hh_reg == now_hh:
            self.open_hour_file()
        else:
            self.auto_create_folder(en)
    def creating_Folder(self,file_type, __Time, T_path_num):  # 0605 修改重複的code
        __time = {0:self.data_path, 1:self.yy_path, 2: self.mm_path, 3: self.dd_path}
        __filepath = __time[T_path_num]
        __fileexist = exists(__filepath)
        if not __fileexist:   # 如果資料夾不存在 (為true)
            try:
                os.mkdir(__filepath, mode=0o777)   # 僅限以數字模式建立資料夾(資料夾只能以數字命名)  0777為限制存取權限
                if file_type == "data":
                    print("       create data folder done.")
                elif file_type == "time":
                    print("       create folder %d done." % __Time)
            except OSError as ose:
                raise OSError("OS is error : %s." % str(ose))

    def create_data_folder(self, en=False):
        if en:
            self.creating_Folder("data", 0, 0)

    def create_year_folder(self):
        self.yy = datetime.now().year  # 年的數值
        self.yy_path = self.data_path + '/' + str(self.yy)
        self.creating_Folder("year", self.yy, 1)

    def create_month_folder(self):
        self.mm = datetime.now().month
        self.mm_path = self.yy_path + '/' + str(self.mm)
        self.creating_Folder("month", self.mm, 2)

    def create_day_folder(self):
        self.dd = datetime.now().day
        self.dd_path = self.mm_path + '/' + str(self.dd)
        self.creating_Folder("day", self.dd, 3)

    def auto_create_folder(self, en=False):
        if en:
            self.create_year_folder()
            self.create_month_folder()
            self.create_day_folder()
            self.open_hour_file()

    def open_hour_file(self):
        data = datetime.now()
        self.hh = data.hour
        MM = data.minute
        ss = data.second
        # file_name = self.dd_path + '/' + str(self.hh).zfill(2) + str(MM).zfill(2) + str(ss).zfill(2)
        file_name = self.dd_path + '/' + str(self.yy) + str(self.mm).zfill(2) + str(self.dd).zfill(2) + '_' + \
                    str(self.hh).zfill(2) + str(MM).zfill(2) + str(ss).zfill(2)     # zfill為在該字串的左邊添加0
        file_exist = (self.hh == self.hh_reg)
        if not file_exist:
            if self.start:  # 當啟用時，檔案還未開啟，所以不用關檔案
                self.start = False
            else:
                self.close_hour_folder()
            self.hh_path = file_name + '.txt'
            self.__data_manager.name = self.hh_path
            self.__data_manager.open(True)   # 建新檔案
            self.write_line('time,wx,wy,wz,ax,ay,az,yy,MM,dd,hh,mm,ss,ms')
            print('     create hour file %s done.' % self.__data_manager.name)
        self.hh_reg = self.hh

    def close_hour_folder(self):
        self.__data_manager.close()
        print('     close hour file %s done.' % self.__data_manager.name)
        pass

    def write_line(self, comment):   # 呼叫寫進txt檔案的method
        self.__data_manager.write_line(comment)

    def saveData(self, datalist, fmt):
        self.__data_manager.saveData(datalist, fmt)

    @property
    def data_path(self):
        return self.__data_path + '/' + 'data'

    @data_path.setter
    def data_path(self, path):
        self.__data_path = path

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, val):
        self.__start = val

if __name__ == "__main__":
    t = atSave_PC()
