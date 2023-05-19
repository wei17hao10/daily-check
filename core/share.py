import json
import os
import shutil

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from datetime import datetime, timedelta
import pandas as pd


class MySignals(QObject):
    update_item_config = pyqtSignal(bool)
    update_execution_result = pyqtSignal(QTreeWidgetItem, list)
    display_error = pyqtSignal(str)
    load_check_result = pyqtSignal(str)
    save_check_result = pyqtSignal(str)
    close_further_check = pyqtSignal(object)
    update_check_all = pyqtSignal(bool)

# class ExecutionSignal(QObject):
#     update_execution_result = pyqtSignal(QTreeWidgetItem, list)
#     display_error = pyqtSignal(str)


class SI:
    mainWin = None
    loginWin = None
    dbCfg = {}
    userinfo = {}
    subWinTable = {}
    ITEM_TYPE = ['SQL', 'Manual']
    user = ''
    strToday = datetime.now().strftime('%Y-%m-%d')
    strTodayTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    CheckItems = []
    itemDF = None
    ChecksTodayNames = []
    ChecksToday = {}
    Checks1Day = {}
    Checks2Day = {}
    Checks3Day = {}
    globalSignal = MySignals()

    @staticmethod
    def loadDBCfgFile():
        if os.path.exists('conf/dbcfg.json'):
            with open('conf/dbcfg.json', encoding='utf8') as f:
                SI.dbCfg = json.load(f)

    @staticmethod
    def loadUsersFile():
        if os.path.exists('conf/users.json'):
            with open('conf/users.json', encoding='utf8') as f:
                SI.userinfo = json.load(f)


class CheckItem:
    def __init__(self, filepath):
        self.itemname = ''
        self.status = ''
        self.type = ''
        self.background = ''
        self.check = ['', '0']
        self.obcondition = ''
        self.jbqcondition = ''
        self.operations = ''
        self.createdBy = ''
        self.createdDate = None
        self.updatedBy = ''
        self.updatedDate = None
        self.sortOrder = 9

        self.filepath = filepath
        self.checkitem = {}

        try:
            self.load_check_item()
        except:
            QMessageBox.warning(SI.mainWin, 'Error', f'load file {filepath} failed')

    def load_check_item(self):
        if os.path.exists(self.filepath) and self.filepath[-5:] == '.json':
            with open(self.filepath, encoding='utf8') as f:
                self.checkitem = json.load(f)
            self.itemname = self.checkitem["CheckName"]
            self.status = self.checkitem["Status"]
            self.type = self.checkitem["Type"]
            self.background = self.checkitem["Background"]
            self.check = self.checkitem["CheckContent"]
            self.obcondition = self.checkitem["OBCondition"]
            self.jbqcondition = self.checkitem["JBQCondition"]
            self.operations = self.checkitem["Operations"]
            self.createdBy = self.checkitem["CreatedBy"]
            self.createdDate = self.checkitem["CreatedDate"]
            self.updatedBy = self.checkitem["UpdatedBy"]
            self.updatedDate = self.checkitem["UpdatedDate"]
            self.sortOrder = self.checkitem["SortOrder"]

    def save_check_item(self):
        self.checkitem = {'CheckName': self.itemname,
                          'Status': self.status,
                          'Type': self.type,
                          'Background': self.background,
                          'CheckContent': self.check,
                          'OBCondition': self.obcondition,
                          'JBQCondition': self.jbqcondition,
                          'Operations': self.operations,
                          'CreatedBy': self.createdBy,
                          'CreatedDate': self.createdDate,
                          'UpdatedBy': self.updatedBy,
                          'UpdatedDate': self.updatedDate,
                          'SortOrder': self.sortOrder
                          }
        with open(self.filepath, 'w+', encoding='utf8') as f:
            json.dump(self.checkitem, f, indent=4)

    def update_background(self, content):
        if self.background != content:
            self.background = content

    def update_check(self, content):
        if self.check[0] != content[0]:
            self.check[0] = content[0]
        if self.check[1] != content[1]:
            self.check[1] = content[1]

    def update_obc(self, content):
        if self.obcondition != content:
            self.obcondition = content

    def update_jbqc(self, content):
        if self.jbqcondition != content:
            self.jbqcondition = content

    def update_operations(self, content):
        if self.operations != content:
            self.operations = content

    def update_info(self, updatedBy, updatedDate):
        self.updatedBy = updatedBy
        self.updatedDate = updatedDate
        ItemMgt.update_itemdf()


class ItemMgt:
    @staticmethod
    def load_all_items():
        if len(SI.CheckItems) == 0:
            dirs = os.listdir('./Checks')
            for folder in SI.ITEM_TYPE:
                if folder in dirs:
                    files = os.listdir(f'Checks/{folder}')
                    files.sort()
                    for file in files:
                        filepath = f'./Checks/{folder}/{file}'
                        item = CheckItem(filepath)
                        SI.CheckItems.append(item)

                    ItemMgt.update_itemdf()

    @staticmethod
    def update_itemdf():
        iteminfo = [[idx,
                     item.type,
                     item.itemname,
                     item.status,
                     item.createdBy,
                     item.createdDate,
                     item.updatedBy,
                     item.updatedDate,
                     item.sortOrder
                     ] for idx, item in enumerate(SI.CheckItems)]
        iteminfo = pd.DataFrame(iteminfo,
                                columns=['id', 'type', 'name', 'status', 'createdBy', 'createdDate',
                                         'updatedBy', 'updatedDate', 'sortOrder'])
        # iteminfo = iteminfo[iteminfo['status'] == 'active']
        iteminfo.sort_values(['type', 'sortOrder', 'createdDate'], inplace=True)
        SI.itemDF = iteminfo

    @staticmethod
    def save_new_item(item_json):
        itemname = item_json["CheckName"]
        itemtype = item_json["Type"]
        filepath = f'./Checks/{itemtype}/{itemname}.json'
        with open(filepath, 'w+', encoding='utf8') as f:
            json.dump(item_json, f, indent=4)

        item = CheckItem(filepath)
        SI.CheckItems.append(item)
        ItemMgt.update_itemdf()

    # @staticmethod
    # def load_item(filepath):
    #     if os.path.exists(filepath):
    #         item = CheckItem(filepath)
    #         SI.CheckItems.append(item)

    @staticmethod
    def delete_item(item):
        os.remove(item.filepath)
        SI.CheckItems.remove(item)
        ItemMgt.update_itemdf()

    @staticmethod
    def get_item(itemname) -> CheckItem:
        CurrentItem = None
        for item in SI.CheckItems:
            if item.itemname == itemname:
                CurrentItem = item
                break
        return CurrentItem


class CheckResult:
    @staticmethod
    def load_result():
        dayoffset = [[0, 3, 4, 5], [1, 1, 4, 5], [2, 1, 2, 5], [3, 1, 2, 3], [4, 1, 2, 3], [5, 1, 2, 3], [6, 2, 3, 4]]
        dayidx = datetime.now().weekday()
        day1ago = (datetime.now() + timedelta(days=-dayoffset[dayidx][1])).strftime('%Y-%m-%d')
        day2ago = (datetime.now() + timedelta(days=-dayoffset[dayidx][2])).strftime('%Y-%m-%d')
        day3ago = (datetime.now() + timedelta(days=-dayoffset[dayidx][3])).strftime('%Y-%m-%d')
        hpath = './History/Recent'
        files = os.listdir(hpath)
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(hpath, f)), reverse=True)
        for fn in files:
            if day1ago in fn and fn.endswith('.json') and SI.Checks1Day == {}:
                try:
                    with open(f'{hpath}/{fn}', encoding='utf8') as f:
                        SI.Checks1Day = json.load(f)
                except:
                    SI.globalSignal.load_check_result.emit('load check result day1 failed')
            elif day2ago in fn and fn.endswith('.json') and SI.Checks2Day == {}:
                try:
                    with open(f'{hpath}/{fn}', encoding='utf8') as f:
                        SI.Checks2Day = json.load(f)
                except:
                    SI.globalSignal.load_check_result.emit('load check result day2 failed')
            elif day3ago in fn and fn.endswith('.json') and SI.Checks3Day == {}:
                try:
                    with open(f'{hpath}/{fn}', encoding='utf8') as f:
                        SI.Checks3Day = json.load(f)
                except:
                    SI.globalSignal.load_check_result.emit('load check result day3 failed')

        CheckResult.move_history()

    @staticmethod
    def move_history():
        spath = './History/Recent'
        dpath = './History'
        thresday = (datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%d')
        files = os.listdir(spath)
        for fn in files:
            name = fn.split()
            if thresday > name[0]:
                shutil.move(f'{spath}/{fn}', f'{dpath}/{fn}')

    @staticmethod
    def get_today_names():
        hpath = './History/Recent'
        files = os.listdir(hpath)
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(hpath, f)), reverse=True)
        SI.ChecksTodayNames = []
        for fn in files:
            if SI.strToday in fn and fn.endswith('.json'):
                SI.ChecksTodayNames.append(
                    {"fileName": fn,
                     # "createdDate": datetime.fromtimestamp(os.path.getctime(os.path.join(hpath, fn))).strftime('%Y-%m-%d %H:%M:%S'),
                     "createdDate": os.path.getctime(os.path.join(hpath, fn)),
                     "updatedDate": os.path.getmtime(os.path.join(hpath, fn))
                     }
                )

    @staticmethod
    def load_today_check(user):
        hpath = './History/Recent'
        files = os.listdir(hpath)
        for fn in files:
            if SI.strToday in fn and user in fn and fn.endswith('.json'):
                try:
                    with open(f'{hpath}/{fn}', encoding='utf8') as f:
                        SI.ChecksToday = json.load(f)
                    break
                except:
                    SI.globalSignal.load_check_result.emit('load today\'s check result failed')

        if SI.ChecksToday == {}:
            return False
        else:
            return True

    @staticmethod
    def save_result():
        hpath = './History/Recent'
        try:
            with open(f'{hpath}/{SI.strToday} - {SI.user}.json', 'w+', encoding='utf8') as f:
                json.dump(SI.ChecksToday, f, indent=4)
        except:
            SI.globalSignal.save_check_result.emit('save check result for today failed')

    @staticmethod
    def get_check(check_name, checks):
        current_check = None
        if checks == {}:
            return None
        for check in checks["check_content"]:
            if check_name == check["check_name"]:
                current_check = check
                break
        return current_check
        # check字典内的取值如果出现问题，程序就卡死啊