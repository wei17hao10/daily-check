import json
import re
import pymssql
import pyperclip as cpb
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QMdiSubWindow, QTableWidgetItem, QTreeWidgetItem, QInputDialog, QLineEdit, \
    QAbstractItemView, QHeaderView, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor

import UI.further_check
from lib.share import SI, ItemMgt, CheckResult, CheckItem
from datetime import datetime
from time import sleep
from threading import Thread


class Login:
    def __init__(self):
        self.ui = uic.loadUi("UI/login.ui")
        self.ui.loginButton.clicked.connect(self.handle_click)
        # self.ui.loginButton.entered.connect(self.handleclk)

    def handle_click(self):
        # print('handle click')
        luser = self.ui.lineUser.text()
        # print('luser=', luser)
        userlist = []
        # print('userinfo', SI.userinfo)
        for user in SI.userinfo['Users']:
            userlist.append(user['username'])
        # print('userlist', userlist)
        if luser in userlist:
            SI.user = luser
            self.ui.hide()
            if SI.mainWin is None:
                SI.mainWin = Main_window()
            else:
                SI.mainWin.put_actions()
            SI.mainWin.ui.show()
        else:
            # print('error username')
            QMessageBox.warning(self.ui, 'Warning', f'User info is not correct.')


class UserConfig:
    def __init__(self):
        self.ui = uic.loadUi("UI/adduser.ui")
        self.users = SI.userinfo['Users']
        self.item2data = {}
        self.load_user_to_tree()

        self.ui.btn_AddUser.clicked.connect(self.add_user)
        self.ui.btn_DelUser.clicked.connect(self.delete_user)
        self.ui.userTree.itemChanged.connect(self.update_user)

    def update_user(self, item, col):
        username = item.text(0)
        user = self.item2data[username]
        if col == 2:
            user['execution'] = item.checkState(col)
        elif col == 3:
            user['configuration'] = item.checkState(col)
        self.save_user_to_file()

    def load_user_to_tree(self):
        tree = self.ui.userTree
        tree.clear()
        self.item2data = {}
        root = tree.invisibleRootItem()
        for user in self.users:
            userItem = QTreeWidgetItem()
            userItem.setText(0, user['username'])
            userItem.setText(1, user['joindate'])
            userItem.setCheckState(2, user['execution'])
            userItem.setCheckState(3, user['configuration'])
            root.addChild(userItem)
            userItem.setExpanded(True)
            self.item2data[user['username']] = user

    def save_user_to_file(self):
        userinfo = {'Users': self.users,
                    'UpdateDate': datetime.now().strftime('%Y-%m-%d')
                    }
        SI.userinfo = userinfo
        with open('config/users.json', 'w+', encoding='utf8') as f:
            json.dump(userinfo, f, indent=4)

    def add_user(self):
        # print('add user')
        username, okPressed = QInputDialog.getText(self.ui, "Input Info", "New Username:", QLineEdit.Normal, "")
        # print('username:', username)
        if okPressed:
            # print('OK clicked')
            user = {"username": username,
                    "joindate": datetime.now().strftime('%Y-%m-%d'),
                    "execution": 2,
                    "configuration": 0
                    }
            self.users.append(user)
            self.save_user_to_file()
            self.load_user_to_tree()

    def delete_user(self):
        currItem = self.ui.userTree.currentItem()
        if currItem is None:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            username = currItem.text(0)
            choice = QMessageBox.question(self.ui, 'Confirmation', f'Are you sure you want to delete this user: {username}?')
            if choice == QMessageBox.Yes:
                user = self.item2data[username]
                idx = self.users.index(user)
                self.users.pop(idx)
                self.save_user_to_file()
                self.load_user_to_tree()


class DBConfig:
    DBCFG_ITEMS = ['Server', 'Username', 'Password', 'Schema']

    def __init__(self):
        self.ui = uic.loadUi("UI/dbcfg.ui")
        self.loadCfg2Table()
        self.ui.table_dbcfg.cellChanged.connect(self.dbcfgItemChange)
        self.ui.btn_clearLog.clicked.connect(self.clearLog)
        self.conn = None
        self.ui.btn_testConnection.clicked.connect(self.checkConn)

    def loadCfg2Table(self):
        table = self.ui.table_dbcfg
        for idx, cfgName in enumerate(self.DBCFG_ITEMS):
            table.insertRow(idx)
            item = QTableWidgetItem(cfgName)
            table.setItem(idx, 0, item)
            item.setFlags(Qt.ItemIsEnabled)  # can not change the parameter name
            table.setItem(idx, 1, QTableWidgetItem(SI.dbCfg.get(cfgName, '')))

    def dbcfgItemChange(self, row, col):
        table = self.ui.table_dbcfg
        cfgName = table.item(row, 0).text()
        cfgValue = table.item(row, col).text()
        SI.dbCfg[cfgName] = cfgValue
        self._saveCfgFile()

        logtext = self.ui.text_dbparamlog
        logtext.append(f'{cfgName}: {cfgValue}')
        logtext.ensureCursorVisible()

    def _saveCfgFile(self):
        with open('config/dbcfg.json', 'w+', encoding='utf8') as f:
            json.dump(SI.dbCfg, f, indent=4)

    def clearLog(self):
        logtext = self.ui.text_dbparamlog
        logtext.clear()

    def checkConn(self):
        try:
            conn = pymssql.connect(SI.dbCfg['Server'], SI.dbCfg['Username'], SI.dbCfg['Password'],
                                   SI.dbCfg['Schema'])
        except pymssql.Error:
            QMessageBox.warning(self.ui, 'Warning', 'Connection failed, please check the configuration.')
        else:
            QMessageBox.information(self.ui, 'Info', f'Database connect successfully.')
            conn.close()


class CheckItemConfig:
    def __init__(self):
        self.ui = uic.loadUi("UI/itemconfwidget.ui")
        self.headerName = {}
        self.get_header_map()

        self.load_item_info()
        # self.ui.actionAdd_Item.triggered.connect(self.load_add_item)
        # self.ui.actionModify_Item.triggered.connect(self.modify_item)
        # self.ui.actionDelete_Item.triggered.connect(self.deleteItem)
        # self.ui.actionDeactivate_Item.triggered.connect(self.deactivateItem)
        # self.ui.actionActivate_Item.triggered.connect(self.activateItem)

        self.ui.btn_Add.clicked.connect(self.load_add_item)
        self.ui.btn_Edit.clicked.connect(self.modify_item)
        self.ui.btn_Delete.clicked.connect(self.delete_item)
        self.ui.btn_Deactivate.clicked.connect(self.deactivate_item)
        self.ui.btn_Activate.clicked.connect(self.activate_item)
        self.ui.btn_Refresh.clicked.connect(self.refresh_display)
        self.ui.itemTree.itemDoubleClicked.connect(self.set_sort_editable)
        self.ui.itemTree.itemChanged.connect(self.sort_changed)

        # self.ms = MySignals()
        # self.ms.update_item_config.connect(self.load_item_info)
        SI.globalSignal.update_item_config.connect(self.load_item_info)
        self.additem = None
        self.mItem = None

    def get_header_map(self):
        ColCount = self.ui.itemTree.headerItem().columnCount()
        num2name = {}
        for i in range(ColCount):
            num2name[str(i)] = self.ui.itemTree.headerItem().text(i)
        self.headerName = {num2name[key]: int(key) for key in num2name.keys()}
        # {
        # 'Item Name': 0,
        # 'Sort Order': 1,
        # 'Created By': 2,
        # 'Created Date': 3,
        # 'Updated By': 4,
        # 'Updated Date': 5
        # }

    def set_sort_editable(self, item, col):
        if col == self.headerName['Sort Order']:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        else:
            item.setFlags(item.flags() & ~ Qt.ItemIsEditable)

    def sort_changed(self, tree_item, col):
        if col == self.headerName['Sort Order']:
            curritem = ItemMgt.get_item(tree_item.text(self.headerName['Item Name']))
            sorder = tree_item.text(col)
            pattern = '^[1-9]$'
            res = re.fullmatch(pattern, sorder)
            if res is None:
                QMessageBox.warning(self.ui, 'Warning', 'Number should between 1~9.')
                tree_item.setText(col, curritem.sortOrder)
            else:
                curritem.sortOrder = sorder
                curritem.save_check_item()

    def refresh_display(self):
        ItemMgt.update_itemdf()
        self.load_item_info()

    def load_item_info(self):
        self.ui.itemTree.clear()
        self.load_item_type('Manual')
        self.load_item_type('SQL')

        self.ui.itemTree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def load_item_type(self, itemtype):
        items = SI.itemDF[SI.itemDF['type'] == itemtype].values
        tree = self.ui.itemTree
        root = tree.invisibleRootItem()
        folderItem = QTreeWidgetItem()
        folderIcon = QIcon("./images/folder.png")
        # 设置节点图标
        folderItem.setIcon(self.headerName['Item Name'], folderIcon)
        # 设置该节点  第1个column 文本
        folderItem.setText(self.headerName['Item Name'], itemtype)
        # 添加到树的不可见根节点下，就成为第一层节点
        root.addChild(folderItem)
        # 设置该节点为展开状态
        folderItem.setExpanded(True)
        for item in items:
            leafItem = QTreeWidgetItem()
            folderItem.addChild(leafItem)
            leafItem.setText(self.headerName['Item Name'], item[2])
            leafItem.setText(self.headerName['Created By'], item[4])
            leafItem.setTextAlignment(self.headerName['Created By'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Created Date'], item[5])
            leafItem.setTextAlignment(self.headerName['Created Date'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Updated By'], item[6])
            leafItem.setTextAlignment(self.headerName['Updated By'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Updated Date'], item[7])
            leafItem.setTextAlignment(self.headerName['Updated Date'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Sort Order'], str(item[8]))
            leafItem.setTextAlignment(self.headerName['Sort Order'], Qt.AlignVCenter | Qt.AlignHCenter)

            if item[3] == 'active':
                leafIcon = QIcon("./images/active item.png")
                leafItem.setIcon(self.headerName['Item Name'], leafIcon)
                leafItem.setForeground(self.headerName['Item Name'], QColor('black'))
            elif item[3] == 'inactive':
                leafIcon = QIcon("./images/deactived item.png")
                leafItem.setIcon(self.headerName['Item Name'], leafIcon)
                leafItem.setForeground(self.headerName['Item Name'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Created By'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Created Date'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Updated By'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Updated Date'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Sort Order'], QColor(180, 180, 180))
            else:
                leafItem.setForeground(self.headerName['Item Name'], QColor(220, 220, 220))

    def load_add_item(self):
        self.additem = AddItem()
        self.additem.ui.show()

    def modify_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)

            self.mItem = ModifyItem(curritem)
            self.mItem.ui.show()

    def delete_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)

            ItemMgt.delete_item(curritem)
            self.load_item_info()

    def deactivate_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)
            if curritem.status == 'active':
                curritem.status = 'inactive'
                curritem.save_check_item()
                ItemMgt.update_itemdf()
                # set icon and color
                leafIcon = QIcon("./images/deactived item.png")
                currentItem.setIcon(self.headerName['Item Name'], leafIcon)
                currentItem.setForeground(self.headerName['Item Name'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Created By'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Created Date'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Updated By'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Updated Date'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Sort Order'], QColor(180, 180, 180))

            elif curritem.status == 'inactive':
                QMessageBox.information(self.ui, 'Info', 'The item is already inactive')

    def activate_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)
            if curritem.status == 'inactive':
                curritem.status = 'active'
                curritem.save_check_item()
                ItemMgt.update_itemdf()
                # set icon and color
                leafIcon = QIcon("./images/active item.png")
                currentItem.setIcon(self.headerName['Item Name'], leafIcon)
                currentItem.setForeground(self.headerName['Item Name'], QColor('black'))
                currentItem.setForeground(self.headerName['Created By'], QColor('black'))
                currentItem.setForeground(self.headerName['Created Date'], QColor('black'))
                currentItem.setForeground(self.headerName['Updated By'], QColor('black'))
                currentItem.setForeground(self.headerName['Updated Date'], QColor('black'))
                currentItem.setForeground(self.headerName['Sort Order'], QColor('black'))

            elif curritem.status == 'active':
                QMessageBox.information(self.ui, 'Info', 'The item is already active')


class AddItem:
    # def __init__(self, ms):
    def __init__(self):
        self.ui = uic.loadUi("./UI/additemwidget.ui")
        self.background = ''
        self.check = ['', '0']
        self.obcondition = ''
        self.jbqcondition = ''
        self.operations = ''
        self.type = ''
        self.itemname = ''
        self.status = 'active'
        self.createdBy = SI.user
        self.createdDate = datetime.now().strftime('%Y-%m-%d')
        self.conn = None
        self.fields = []
        self.rows = []

        # self.ui.lineThreshold.setText(self.check[1])
        self.ui.itemTypeCombo.addItems(SI.ITEM_TYPE)
        self.ui.itemTypeCombo.currentIndexChanged.connect(self.handle_selection_change)
        self.ui.btn_OK.clicked.connect(self.ok_clicked)
        self.ui.btn_cancel.clicked.connect(self.cancel_clicked)
        self.ui.btn_execute.clicked.connect(self.execute_sql)
        self.ui.btn_checkres.clicked.connect(self.display_result)
        self.ui.lineThreshold.setText(self.check[1])

    def execute_sql(self):
        self.create_db_conn()
        cursor = self.conn.cursor()
        sql = self.ui.checkSQLText.toPlainText()
        try:
            cursor.execute(sql)
            self.fields = [field[0] for field in cursor.description]
            self.rows = cursor.fetchall()
        except pymssql.ProgrammingError:
            QMessageBox.warning(self.ui, 'Warning', 'Programming Error, please check the SQL.')
        except pymssql.Error:
            QMessageBox.warning(self.ui, 'Warning', 'General Error')
        else:
            QMessageBox.information(self.ui, 'Info', f'SQL execute successfully. Row number is {len(self.rows)}')

    def display_result(self):
        tab = DisplaySQLResult(self.fields, self.rows)
        tab.ui.exec_()

    def handle_selection_change(self):
        combotext = self.ui.itemTypeCombo.currentText()
        if combotext in SI.ITEM_TYPE:
            idx = SI.ITEM_TYPE.index(combotext)
            self.ui.stackedAddInfo.setCurrentIndex(idx)

    def check_text(self):
        # print('check text')
        self.type = self.ui.itemTypeCombo.currentText()
        if self.type == 'SQL':
            self.background = self.ui.SQLBackgroundText.toPlainText()
            self.check[0] = self.ui.checkSQLText.toPlainText()
            self.check[1] = self.ui.lineThreshold.text()
            self.operations = self.ui.SQLOpsText.toPlainText()
            # print('after ops')
            if len(self.background) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input background info.')
                return False
            elif len(self.check[0]) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input SQL.')
                return False
            elif not self.check[1].isdigit():
                QMessageBox.warning(self.ui, 'Warning', 'Threshold is not a number.')
                return False
            elif len(self.operations) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input Operations steps when check failed.')
                return False
            else:
                # print('true')
                return True
        elif self.type == 'Manual':
            self.background = self.ui.MBackgroundText.toPlainText()
            self.check[0] = self.ui.MCheckProcessText.toPlainText()
            self.operations = self.ui.MOpsText.toPlainText()
            if len(self.background) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input background info.')
                return False
            elif len(self.check[0]) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input manual check process.')
                return False
            elif len(self.operations) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input Operations steps when check failed.')
                return False
            else:
                return True

    def check_name(self):
        self.itemname = self.ui.itemNameLine.text()
        pattern = '^[a-zA-Z0-9][a-zA-Z0-9 :\-_]*$'
        res = re.fullmatch(pattern, self.itemname)
        if res is None:
            QMessageBox.warning(self.ui, 'Warning', 'Please check the item name.')
            return False
        return True

    def save_2_file(self):
        # self.itemname = self.ui.itemNameLine.text()
        checkcontent = {'CheckName': self.itemname,
                        'Status': self.status,
                        'Type': self.type,
                        'Background': self.background,
                        'CheckContent': self.check,
                        'OBCondition': self.obcondition,
                        'JBQCondition': self.jbqcondition,
                        'Operations': self.operations,
                        'CreatedBy': self.createdBy,
                        'CreatedDate': self.createdDate,
                        'UpdatedBy': self.createdBy,
                        'UpdatedDate': self.createdDate,
                        'SortOrder': '9'
                        }
        ItemMgt.save_new_item(checkcontent)

    def ok_clicked(self):
        if self.check_name() and self.check_text():
            self.save_2_file()
            self.close_db_conn()
            self.ui.close()
            # print('ui close successfully')
            # self.ms.update_item_config.emit(True)
            SI.globalSignal.update_item_config.emit(True)

    def cancel_clicked(self):
        self.close_db_conn()
        self.ui.close()

    def create_db_conn(self):
        if self.conn is None:
            try:
                self.conn = pymssql.connect(SI.dbCfg['Server'], SI.dbCfg['Username'], SI.dbCfg['Password'],
                                            SI.dbCfg['Schema'])
            except pymssql.InterfaceError:
                QMessageBox.warning(self.ui, 'Error', 'Connection Error')

    def close_db_conn(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None


class DisplaySQLResult:
    def __init__(self, fields, rows):
        self.ui = uic.loadUi("./UI/sqlresult.ui")
        self.fields = fields
        self.rows = rows
        self.set_content()

    def set_content(self):
        fieldlen = len(self.fields)
        rowlen = len(self.rows)
        tableWidget = self.ui.tableSQLResult
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tableWidget.setColumnCount(fieldlen)
        if rowlen >= 500:
            rowlen = 500
            self.rows = self.rows[:500]
        tableWidget.setRowCount(rowlen)
        tableWidget.setHorizontalHeaderLabels(self.fields)
        for i, row in enumerate(self.rows):
            for j in range(len(self.fields)):
                newItem = QTableWidgetItem(str(row[j]))
                tableWidget.setItem(i, j, newItem)


class ModifyItem(AddItem):
    def __init__(self, item: CheckItem):
        super().__init__()
        self.ui.setWindowTitle('Modify Check Item')
        self.updatedBy = SI.user
        self.updatedDate = datetime.now().strftime('%Y-%m-%d')
        self.item = item
        self.load_item()
        self.setContent()
        self.updatedFlag = 0
        self.ui.SQLBackgroundText.textChanged.connect(self.content_changed)
        self.ui.checkSQLText.textChanged.connect(self.content_changed)
        self.ui.lineThreshold.textChanged.connect(self.content_changed)
        self.ui.SQLOpsText.textChanged.connect(self.content_changed)
        self.ui.MBackgroundText.textChanged.connect(self.content_changed)
        self.ui.MCheckProcessText.textChanged.connect(self.content_changed)
        self.ui.MOpsText.textChanged.connect(self.content_changed)
        self.ui.JBQText.textChanged.connect(self.content_changed)
        self.ui.OBText.textChanged.connect(self.content_changed)

    def load_item(self):
        self.itemname = self.item.itemname
        self.status = self.item.status
        self.type = self.item.type
        self.background = self.item.background
        self.check = self.item.check
        self.obcondition = self.item.obcondition
        self.jbqcondition = self.item.jbqcondition
        self.operations = self.item.operations
        self.createdBy = self.item.createdBy
        self.createdDate = self.item.createdDate

    def setContent(self):
        self.ui.itemNameLine.setReadOnly(True)
        self.ui.itemNameLine.setText(self.itemname)
        self.ui.itemTypeCombo.clear()
        # self.ui.itemTypeCombo.removeItem(0)
        self.ui.itemTypeCombo.addItem(self.type)
        if self.type == 'SQL':
            self.ui.SQLBackgroundText.setText(self.background)
            self.ui.checkSQLText.setText(self.check[0])
            self.ui.lineThreshold.setText(self.check[1])
            self.ui.OBText.setText(self.obcondition)
            self.ui.JBQText.setText(self.jbqcondition)
            self.ui.SQLOpsText.setText(self.operations)
        elif self.type == 'Manual':
            self.ui.MBackgroundText.setText(self.background)
            self.ui.MCheckProcessText.setText(self.check[0])
            self.ui.MOpsText.setText(self.operations)

    def save_2_file(self):
        # self.itemname = self.ui.itemNameLine.text()
        if self.updatedFlag == 1:
            # self.background = self.ui.SQLBackgroundText.toPlainText() if self.type == 'SQL' else self.ui.MBackgroundText.toPlainText()
            # self.check[0] = self.ui.checkSQLText.toPlainText() if self.type == 'SQL' else self.ui.MCheckProcessText.toPlainText()
            # self.operations = self.ui.SQLOpsText.toPlainText() if self.type == 'SQL' else self.ui.MOpsText.toPlainText()
            self.obcondition = self.ui.OBText.toPlainText()
            self.jbqcondition = self.ui.JBQText.toPlainText()

            self.item.update_background(self.background)
            self.item.update_check(self.check)
            self.item.update_obc(self.obcondition)
            self.item.update_jbqc(self.jbqcondition)
            self.item.update_operations(self.operations)
            self.item.update_info(self.updatedBy, self.updatedDate)
            self.item.save_check_item()
            self.updatedFlag = 0

    def content_changed(self):
        self.updatedFlag = 1


class CheckAllResult:
    def __init__(self):
        self.ui = uic.loadUi("./UI/checkall.ui")
        # self.itemdf = None
        self.itemlist = []
        # self.es = ExecutionSignal()
        self.conn = None
        self.check_content = []
        self.check_date = datetime.now().strftime('%Y-%m-%d')
        self.check_time = ''
        # self.check_result = {}
        self.single_ui = None
        self.execute_flag = False
        self.load_items()
        self.ui.btn_executeAll.clicked.connect(self.execute_all)
        self.ui.btn_loadResult.clicked.connect(self.load_result)
        # self.es.update_execution_result.connect(self.update_result)
        # self.es.display_error.connect(self.display_error)
        SI.globalSignal.update_execution_result.connect(self.update_result)
        SI.globalSignal.display_error.connect(self.display_error)
        SI.globalSignal.load_check_result.connect(self.display_error)
        SI.globalSignal.save_check_result.connect(self.display_error)
        SI.globalSignal.update_check_all.connect(self.update_tree)
        self.ui.treeResult.itemDoubleClicked.connect(self.open_single_result)

    def load_items(self):
        items = SI.itemDF[SI.itemDF['status'] == 'active']
        items = items.values

        tree = self.ui.treeResult
        tree.clear()
        root = tree.invisibleRootItem()
        self.itemlist = []

        for item in items:
            leaf_item = QTreeWidgetItem()
            root.addChild(leaf_item)
            leaf_item.setText(0, item[2])
            leaf_item.setForeground(0, QColor(150, 150, 150))

            leaf_item.setText(1, item[1])
            leaf_item.setForeground(1, QColor(150, 150, 150))
            leaf_item.setTextAlignment(1, Qt.AlignVCenter | Qt.AlignHCenter)

            leaf_item.setText(2, 'ready')
            leaf_item.setForeground(2, QColor(150, 150, 150))
            leaf_item.setTextAlignment(2, Qt.AlignVCenter | Qt.AlignHCenter)

            self.itemlist.append(leaf_item)

        self.ui.treeResult.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def execute_all(self):
        self.load_items()
        self.check_content = []
        self.check_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ui.lineUser.setReadOnly(True)
        self.ui.lineUser.setText(SI.user)

        self.ui.lineStart.setReadOnly(True)
        self.ui.lineStart.setText(self.check_time)

        t = Thread(target=self.execute_all_t)
        t.start()

    def execute_all_t(self):
        if not self.create_db_conn():
            return

        self.execute_flag = False

        for item in self.itemlist:
            self.execute_one(item)

        SI.ChecksToday = {"check_user": SI.user,
                          "check_date": self.check_time,
                          "check_content": self.check_content}
        # self.save_result()
        CheckResult.save_result()
        CheckResult.load_result()
        self.execute_flag = True

    # def save_result(self):
    #     try:
    #         with open(f'History/{self.check_date} - {SI.user}.json', 'w+', encoding='utf8') as f:
    #             json.dump(self.check_result, f, indent=4)
    #     except:
    #         QMessageBox.warning(self.ui, 'Error', 'Save result file failed')

    def execute_one(self, item):
        item_name = item.text(0)
        si_item = ItemMgt.get_item(item_name)
        item_type = si_item.type
        check_result = 'no operation'
        rowlen = 0
        display_res = []
        if si_item.type == 'Manual':
            display_res = ['need to check', '-', check_result]
        elif si_item.type == 'SQL':
            rowlen = self.execute_sql(si_item.check[0])
            if 0 <= rowlen <= int(si_item.check[1]):
                check_result = 'auto pass'
                display_res = ['executed', 'pass', check_result]
            elif rowlen > 0:
                display_res = ['executed', 'fail', check_result]
            elif rowlen == -1:
                display_res = ['SQL issue', '-', check_result]

        # self.es.update_execution_result.emit(item, display_res)
        SI.globalSignal.update_execution_result.emit(item, display_res)
        sleep(1)
        self.check_content.append({"check_name": item_name,
                                   "item_type": item_type,
                                   "count": rowlen,
                                   "comment": '',
                                   "check_result": display_res})

    def execute_sql(self, sql):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            rowlen = len(cursor.fetchall())
            return rowlen
        except pymssql.ProgrammingError:
            # self.es.display_error.emit('Programming Error, please check the SQL.')
            rowlen = -1
            return rowlen
        except pymssql.Error:
            # self.es.display_error.emit('General Error')
            rowlen = -1
            return rowlen

    def create_db_conn(self):
        sql_flag = False
        items = SI.itemDF.values
        for item in items:
            if item[1] == 'SQL':
                sql_flag = True
                break

        if self.conn is None and sql_flag:
            try:
                self.conn = pymssql.connect(SI.dbCfg['Server'], SI.dbCfg['Username'], SI.dbCfg['Password'],
                                            SI.dbCfg['Schema'])
            except pymssql.Error:
                # self.es.display_error.emit('Database Connection Error')
                SI.globalSignal.display_error.emit('Database Connection Error')
                return False
                # QMessageBox.warning(self.ui, 'Error', 'Database Connection Error')

        return True

    def update_result(self, item, result):
        item.setForeground(0, QColor('black'))
        item.setForeground(1, QColor('black'))
        item.setForeground(2, QColor('black'))
        item.setForeground(3, QColor('black'))

        item.setText(2, result[0])

        if result[1] == 'pass':
            icon = QIcon("./images/executed successful.png")
        elif result[1] == 'fail':
            icon = QIcon("./images/executed failed.png")
        else:
            icon = QIcon("./images/manual.png")
        item.setIcon(3, icon)
        item.setText(3, result[1])
        item.setTextAlignment(3, Qt.AlignVCenter | Qt.AlignHCenter)

        if "Operation Done" == result[2]:
            icon = QIcon("./images/workaround.png")
            item.setIcon(4, icon)
            item.setText(4, result[2])
            item.setTextAlignment(4, Qt.AlignVCenter | Qt.AlignHCenter)
            item.setForeground(4, QColor('black'))
        else:
            icon = QIcon()
            item.setIcon(4, icon)
            item.setText(4, "")

    def display_error(self, error):
        QMessageBox.warning(self.ui, 'Error', error)

    def open_single_result(self, currentItem, vol):
        if not self.execute_flag:
            self.display_error('No execution or execution is not finished.')
            return

        item_name = currentItem.text(0)
        current_check = CheckResult.get_check(item_name, SI.ChecksToday)
        if current_check is None:
            self.display_error('No execution info')
        else:
            self.single_ui = SingleCheckResult(current_check)
            # self.single_ui.ui.show()

    def load_result(self):
        if not self.execute_flag and SI.ChecksToday == {}:
            if CheckResult.load_today_check():
                self.check_content = SI.ChecksToday["check_content"]
                CheckResult.load_result()
                self.ui.lineUser.setReadOnly(True)
                self.ui.lineUser.setText(SI.ChecksToday["check_user"])
                self.ui.lineStart.setReadOnly(True)
                self.ui.lineStart.setText(SI.ChecksToday["check_date"])
                self.update_tree()

                self.execute_flag = True
            else:
                QMessageBox.warning(self.ui, 'Warning', 'There is no execution today. Load Failed.')

    def update_tree(self):
        for item in self.itemlist:
            item_name = item.text(0)
            check = CheckResult.get_check(item_name, SI.ChecksToday)
            self.update_result(item, check["check_result"])


class MyWidget(QWidget):
    def closeEvent(self, event):
        SI.globalSignal.close_further_check.emit(event)
        # SI.globalSignal.close_further_check.emit(True)
        # QMessageBox.Information(self, 'Info', 'close method triggered')
        # event.accept()


class SingleCheckResult:
    def __init__(self, current_check):
        # self.ui = uic.loadUi("UI/further check.ui")
        self.ui = UI.further_check.Ui_Form()
        self.widget = MyWidget()
        self.ui.setupUi(self.widget)

        self.current_check = current_check
        self.conn = None
        self.check_sql = ''
        self.ob_condition = ''
        self.jobq_condition = ''
        self.fields = []
        self.rows = []
        self.day1comment = ''
        self.day2comment = ''
        self.day3comment = ''
        self.check_name = self.current_check["check_name"]
        self.single_exe_flag = False

        self.namelist = [item[2] for item in SI.itemDF[SI.itemDF['status'] == 'active'].values]
        self.btn_style = {
            "grey":     '''QPushButton{color:rgb(180,180,180);font-size:11px;}''',
            "black":    '''QPushButton{color:rgb(30,30,30);font-size:11px;}''',
            "blue":     '''QPushButton{color: #4a86e8;font-size:14px;}'''
        }
        # self.grey_style = '''QPushButton{color:rgb(180,180,180);}'''
        self.ui.btn_check.clicked.connect(self.execute_sql)
        self.ui.btn_result.clicked.connect(self.show_result)
        self.ui.btn_SQL.clicked.connect(self.click_sql)
        self.ui.btn_ob.clicked.connect(self.click_ob)
        self.ui.btn_jobq.clicked.connect(self.click_jobq)
        self.ui.btn_last.clicked.connect(self.click_last)
        self.ui.btn_next.clicked.connect(self.click_next)
        self.ui.btn_close.clicked.connect(self.widget.close)
        self.ui.btn_day1ago.clicked.connect(self.click_previous_1)
        self.ui.btn_day2ago.clicked.connect(self.click_previous_2)
        self.ui.btn_day3ago.clicked.connect(self.click_previous_3)
        # self.ui.textComments.textChanged.connect(self.my_close)
        SI.globalSignal.close_further_check.connect(self.on_close)

        self.load_data()

        self.widget.show()

    def init_again(self, current_check):
        self.current_check = current_check
        # self.conn = None
        self.check_sql = ''
        self.ob_condition = ''
        self.jobq_condition = ''
        self.fields = []
        self.rows = []
        self.day1comment = ''
        self.day2comment = ''
        self.day3comment = ''
        self.check_name = self.current_check["check_name"]
        self.single_exe_flag = False
        # 继续编写初始化内容
        self.load_data()

    def load_data(self):
        # check_name = self.current_check["check_name"]
        result_num = self.current_check["count"]
        item = ItemMgt.get_item(self.check_name)
        created_by = item.createdBy
        updated_by = item.updatedBy
        background = item.background
        operations = item.operations
        self.check_sql = item.check[0]
        self.ob_condition = item.obcondition
        self.jobq_condition = item.jbqcondition

        self.ui.line_itemname.setReadOnly(True)
        self.ui.line_itemname.setText(self.check_name)

        self.ui.line_createdby.setReadOnly(True)
        self.ui.line_createdby.setText(created_by)

        self.ui.line_updatedby.setReadOnly(True)
        self.ui.line_updatedby.setText(updated_by)

        self.ui.textBackgrd.setText(background)
        self.ui.textOperations.setText(operations)

        today_check = CheckResult.get_check(self.check_name, SI.ChecksToday)
        this_comment = today_check["comment"]
        if len(this_comment.strip()) == 0 and today_check["item_type"] == "SQL" and today_check["count"] == 0:
            this_comment = "auto pass"
        self.ui.textComments.setText(this_comment)

        self.ui.line_num.setReadOnly(True)
        self.ui.line_num.setText(str(result_num))

        final = today_check["check_result"][2]
        if final == "Operation Done":
            self.ui.radioOpDone.toggle()
        else:
            self.ui.radioNoOp.toggle()

        self.ui.btn_check.setStyleSheet(self.btn_style["black"])
        self.ui.btn_result.setStyleSheet(self.btn_style["black"])

        if len(self.check_sql.strip()) > 0 and item.type == 'SQL':
            self.ui.btn_SQL.setStyleSheet(self.btn_style["black"])
        else:
            self.ui.btn_SQL.setStyleSheet(self.btn_style["grey"])

        if len(self.ob_condition.strip()) > 0:
            self.ui.btn_ob.setStyleSheet(self.btn_style["black"])
        else:
            self.ui.btn_ob.setStyleSheet(self.btn_style["grey"])

        if len(self.jobq_condition.strip()) > 0:
            self.ui.btn_jobq.setStyleSheet(self.btn_style["black"])
        else:
            self.ui.btn_jobq.setStyleSheet(self.btn_style["grey"])

        first_comment = 0
        if SI.Checks1Day != {}:
            day1check = CheckResult.get_check(self.check_name, SI.Checks1Day)
            if day1check is not None:
                self.day1comment = day1check["comment"]
                if first_comment == 0:
                    first_comment = 1

        if SI.Checks2Day != {}:
            day2check = CheckResult.get_check(self.check_name, SI.Checks2Day)
            if day2check is not None:
                self.day2comment = day2check["comment"]
                if first_comment == 0:
                    first_comment = 2

        if SI.Checks3Day != {}:
            day3check = CheckResult.get_check(self.check_name, SI.Checks3Day)
            if day3check is not None:
                self.day3comment = day3check["comment"]
                if first_comment == 0:
                    first_comment = 3

        # print('first_comment:' + str(first_comment))
        if first_comment == 1:
            self.click_previous_1()
        elif first_comment == 2:
            self.click_previous_2()
        elif first_comment == 3:
            self.click_previous_3()
        else:
            btn_style = self.btn_style["grey"]
            self.ui.btn_day1ago.setStyleSheet(btn_style)
            self.ui.btn_day2ago.setStyleSheet(btn_style)
            self.ui.btn_day3ago.setStyleSheet(btn_style)

    # self.ui.btn_day1ago.setStyleSheet('''
        # QPushButton{border-radius:2px;background:rgb(211,211,211);font-family:'微软雅黑';color:rgb(255,182,193);font-size:18px;}
        # /* 按钮圆角 2个像素              背景颜色                      字体                  字体颜色      字体大小      */
        # QPushButton:hover{border-radius:50px;background:rgb(100,149,237);font-family:'微软雅黑';color:rgb(255,255,255);font-size:16px;}
        # /*鼠标指向按钮后按钮变化*/
        #    ''')

    def execute_sql(self):
        if self.single_exe_flag:
            return

        self.create_db_conn()
        cursor = self.conn.cursor()
        self.single_exe_flag = True
        self.update_btn_color()
        try:
            cursor.execute(self.check_sql)
            self.fields = [field[0] for field in cursor.description]
            self.rows = cursor.fetchall()
        except pymssql.ProgrammingError:
            QMessageBox.warning(self.widget, 'Warning', 'Programming Error, please check the SQL.')
        except pymssql.Error:
            QMessageBox.warning(self.widget, 'Warning', 'General Error')
        else:
            self.ui.line_num.setText(str(len(self.rows)))
        self.single_exe_flag = False
        self.update_btn_color()

    def update_btn_color(self):
        if self.single_exe_flag:
            self.ui.btn_check.setStyleSheet(self.btn_style["grey"])
            self.ui.btn_result.setStyleSheet(self.btn_style["grey"])
        else:
            self.ui.btn_check.setStyleSheet(self.btn_style["black"])
            self.ui.btn_result.setStyleSheet(self.btn_style["black"])

    def show_result(self):
        if self.single_exe_flag:
            return

        if len(self.rows) != 0:
            tab = DisplaySQLResult(self.fields, self.rows)
            tab.ui.exec_()

    def click_sql(self):
        if len(self.check_sql.strip()) > 0 and self.current_check["item_type"] == 'SQL':
            cpb.copy(self.check_sql)
            QMessageBox.information(self.widget, 'Info', 'SQL is copied.')

    def click_ob(self):
        if len(self.ob_condition.strip()) == 0:
            return
        cpb.copy(self.ob_condition)
        QMessageBox.information(self.widget, 'Info', 'OB condition is copied.')

    def click_jobq(self):
        if len(self.jobq_condition.strip()) == 0:
            return
        cpb.copy(self.jobq_condition)
        QMessageBox.information(self.widget, 'Info', 'jobQ condition is copied.')

    def click_last(self):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.widget, 'Warning', 'Operation Comments can not be empty.')
        else:
            self.update_comment()

            i = self.namelist.index(self.check_name)
            if i - 1 < 0:
                QMessageBox.information(self.widget, 'Info', 'This is the first check item.')
            else:
                current_check = CheckResult.get_check(self.namelist[i-1], SI.ChecksToday)
                self.init_again(current_check)

    def click_next(self):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.widget, 'Warning', 'Operation Comments can not be empty.')
        else:
            self.update_comment()

            nlistlen = len(self.namelist)
            i = self.namelist.index(self.check_name)
            if i + 1 < nlistlen:
                current_check = CheckResult.get_check(self.namelist[i+1], SI.ChecksToday)
                self.init_again(current_check)
            else:
                QMessageBox.information(self.widget, 'Info', 'This is the last check item.')

    def on_close(self, event):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.widget, 'Warning', 'Operation Comments can not be empty.')
            event.ignore()
        else:
            self.update_comment()
            self.close_db_conn()
            CheckResult.save_result()
            event.accept()
            SI.globalSignal.update_check_all.emit(True)

    def update_comment(self):
        today_check = CheckResult.get_check(self.check_name, SI.ChecksToday)
        this_comment = self.ui.textComments.toPlainText()
        if today_check["comment"] != this_comment:
            today_check["comment"] = this_comment

        final = "Operation Done" if self.ui.radioOpDone.isChecked() else "No Operation"
        today_check["check_result"][2] = final

    def click_previous_1(self):
        if len(self.day1comment.strip()) == 0:
            return
        self.ui.btn_day1ago.setStyleSheet(self.btn_style["blue"])

        btn_style = self.btn_style["grey"] if len(self.day2comment.strip()) == 0 else self.btn_style["black"]
        self.ui.btn_day2ago.setStyleSheet(btn_style)

        btn_style = self.btn_style["grey"] if len(self.day3comment.strip()) == 0 else self.btn_style["black"]
        self.ui.btn_day3ago.setStyleSheet(btn_style)

        self.ui.textPreComment.setText(self.day1comment)

    def click_previous_2(self):
        if len(self.day2comment.strip()) == 0:
            return
        self.ui.btn_day2ago.setStyleSheet(self.btn_style["blue"])

        btn_style = self.btn_style["grey"] if len(self.day1comment.strip()) == 0 else self.btn_style["black"]
        self.ui.btn_day1ago.setStyleSheet(btn_style)

        btn_style = self.btn_style["grey"] if len(self.day3comment.strip()) == 0 else self.btn_style["black"]
        self.ui.btn_day3ago.setStyleSheet(btn_style)

        self.ui.textPreComment.setText(self.day2comment)

    def click_previous_3(self):
        if len(self.day3comment.strip()) == 0:
            return
        self.ui.btn_day3ago.setStyleSheet(self.btn_style["blue"])

        btn_style = self.btn_style["grey"] if len(self.day1comment.strip()) == 0 else self.btn_style["black"]
        self.ui.btn_day1ago.setStyleSheet(btn_style)

        btn_style = self.btn_style["grey"] if len(self.day2comment.strip()) == 0 else self.btn_style["black"]
        self.ui.btn_day2ago.setStyleSheet(btn_style)

        self.ui.textPreComment.setText(self.day3comment)

    def create_db_conn(self):
        if self.conn is None:
            try:
                self.conn = pymssql.connect(SI.dbCfg['Server'], SI.dbCfg['Username'], SI.dbCfg['Password'],
                                            SI.dbCfg['Schema'])
            except pymssql.InterfaceError:
                QMessageBox.warning(self.widget, 'Error', 'Connection Error')

    def close_db_conn(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None


class Main_window:
    def __init__(self):
        if SI.user == '':
            SI.user = 'admin'
        self.ui = uic.loadUi("UI/mainwin.ui")
        self.ui.actionUser_Config.triggered.connect(self.openUserConfig)
        self.ui.actionDB_Config.triggered.connect(self.openDBConfig)
        self.ui.actionCheck_Item_Config.triggered.connect(self.openCheckItemConfig)
        self.ui.actionExit.triggered.connect(self.exitMain)
        self.ui.actionExecute_all.triggered.connect(self.executeAll)

        self.put_actions()

        ItemMgt.load_all_items()

    def put_actions(self):
        # print(SI.user)
        priv_exe = 2
        priv_conf = 0
        for user in SI.userinfo["Users"]:
            if SI.user == user["username"]:
                priv_exe = user["execution"]
                priv_conf = user["configuration"]
                break

        self.switch_action(priv_conf, self.ui.actionUser_Config)
        self.switch_action(priv_conf, self.ui.actionDB_Config)
        self.switch_action(priv_conf, self.ui.actionCheck_Item_Config)
        self.switch_action(priv_exe, self.ui.actionExecute_all)
        self.switch_action(2, self.ui.actionExit)

    def switch_action(self, priv, action):
        if priv == 0:
            self.ui.menu.removeAction(action)
            self.ui.toolBar.removeAction(action)
        elif priv == 2:
            self.ui.menu.addAction(action)
            self.ui.toolBar.addAction(action)

    def _openSubWindow(self, FuncClass):
        def createSubWin():
            subWin = QMdiSubWindow()
            # subWin.setWindowTitle(str(FuncClass.__name__))
            funcCase = FuncClass()
            subWin.setWidget(funcCase.ui)
            subWin.setAttribute(Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(subWin)
            # 这里添加funcCase共享的原因是：如果不添加，这个实例就会在函数执行完成后被销毁，这样cellchanged信号就找不到回调函数了。
            # 添加subWin共享的原因是，要调用其show函数
            SI.subWinTable[str(FuncClass)] = {'subWin': subWin, 'funcCase': funcCase}
            subWin.show()
            subWin.setWindowState(Qt.WindowActive | Qt.WindowMaximized)

        if str(FuncClass) not in SI.subWinTable:
            createSubWin()
            return

        subWin = SI.subWinTable[str(FuncClass)]['subWin']
        try:
            subWin.show()
            subWin.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
        except:
            createSubWin()

    def openDBConfig(self):
        self._openSubWindow(DBConfig)

    def openCheckItemConfig(self):
        self._openSubWindow(CheckItemConfig)

    def openUserConfig(self):
        self._openSubWindow(UserConfig)

    def exitMain(self):
        self.ui.close()
        SI.loginWin.ui.lineUser.setText('')
        SI.subWinTable = {}
        SI.mainWin = None
        SI.loginWin.ui.show()

    def executeAll(self):
        self._openSubWindow(CheckAllResult)
