from PyQt5 import uic
from core.share import SI, ItemMgt, CheckResult
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QHeaderView
from datetime import datetime
import pymssql
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from threading import Thread
from time import sleep, timezone
from core.single_check import SingleCheckResult
from core.powershell import PowerShell
from runpy import run_path
import os


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
        self.is_hide_passed: bool = True
        self.load_items()
        self.load_all_resinfo()
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
        self.ui.rb_hidePass.toggled.connect(self.rb_hide_passed_toggled)

    def rb_hide_passed_toggled(self, checked):
        self.is_hide_passed = checked

    def load_all_resinfo(self):
        CheckResult.get_today_names()
        # print(SI.ChecksTodayNames)
        for n in SI.ChecksTodayNames:
            user = n['fileName'].split('.')[0].split()[-1]
            time = datetime.fromtimestamp(n['updatedDate']).strftime('%H:%M:%S')
            self.ui.cbox_history.addItem(f'{time} - {user}')

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
        # self.check_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.check_time = datetime.fromtimestamp(datetime.now().timestamp() + timezone).strftime('%Y-%m-%d %H:%M:%S')

        self.ui.lineUser.setReadOnly(True)
        self.ui.lineUser.setText(SI.user)

        local_time = datetime.fromtimestamp(datetime.strptime(self.check_time, '%Y-%m-%d %H:%M:%S').timestamp() - timezone).strftime('%Y-%m-%d %H:%M:%S')
        self.ui.lineStart.setReadOnly(True)
        self.ui.lineStart.setText(local_time)

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
        comment = ''
        display_res = []
        if si_item.type == 'Manual':
            display_res = ['need to check', '-', check_result]
        elif si_item.type == 'SQL':
            rowlen = self.execute_sql(si_item.check[0])
            if 0 <= rowlen <= int(si_item.check[1]):
                check_result = 'auto pass'
                comment = check_result
                display_res = ['executed', 'pass', check_result]
            elif rowlen > int(si_item.check[1]):
                display_res = ['executed', 'fail', check_result]
            elif rowlen == -1:
                display_res = ['SQL issue', '-', check_result]
        elif si_item.type == 'Powershell':
            ps_cmd = si_item.check[0]
            # print(ps_cmd)
            with PowerShell('GBK') as ps:
                outs, errs = ps.run(ps_cmd)
            outs = str(outs)
            errs = str(errs)
            res = 'Output:\n' + outs + '\nErrors:\n' + errs

            if self.validate_result(res, si_item):
                check_result = 'auto pass'
                comment = check_result
                display_res = ['executed', 'pass', check_result]
            else:
                rowlen = -1
                display_res = ['executed', 'fail', check_result]

        elif si_item.type == 'Python':
            script_dir = 'Checks/pyscripts/execute'
            script_file = item_name + '.py'
            script_path = os.path.join(script_dir, script_file)

            try:
                result = run_path(path_name=script_path)
            except:
                rowlen = -1
                display_res = ['executed', 'fail', check_result]
                return

            if self.validate_result(result['output'], si_item):
                check_result = 'auto pass'
                comment = check_result
                display_res = ['executed', 'pass', check_result]
            else:
                rowlen = -1
                display_res = ['executed', 'fail', check_result]

        # self.es.update_execution_result.emit(item, display_res)
        SI.globalSignal.update_execution_result.emit(item, display_res)
        sleep(1)
        self.check_content.append({"check_name": item_name,
                                   "item_type": item_type,
                                   "count": rowlen,
                                   "comment": comment,
                                   "check_result": display_res})

    def validate_result(self, output, si_item):
        script_dir = 'Checks/pyscripts/check_output'
        script_file = si_item.itemname + '.py'
        script_path = os.path.join(script_dir, script_file)
        result = {}

        if os.path.exists(script_path):
            check_params = {'output': output}
            try:
                result = run_path(path_name=script_path, init_globals=check_params)
            except:
                QMessageBox.warning(self.ui, 'warning', 'Script execution failed, please check!')

            if 'isPass' in result:
                if isinstance(result['isPass'], bool):
                    return result['isPass']
                else:
                    return False
            else:
                return False
        else:
            return False

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
            item.setTextAlignment(4, Qt.AlignVCenter | Qt.AlignLeft)
            item.setForeground(4, QColor('black'))
        else:
            icon = QIcon()
            item.setIcon(4, icon)
            item.setText(4, "")

    def display_error(self, error):
        QMessageBox.warning(self.ui, 'Error', error)

    def open_single_result(self, current_item, vol):
        if not self.execute_flag:
            self.display_error('No execution or execution is not finished.')
            return

        item_name = current_item.text(0)
        current_check = CheckResult.get_check(item_name, SI.ChecksToday)
        if current_check is None:
            self.display_error('No execution info')
        else:
            self.single_ui = SingleCheckResult(current_check, self.is_hide_passed)
            self.single_ui.ui.show()

    def load_result(self):
        # if not self.execute_flag and SI.ChecksToday == {}:
        if not self.execute_flag:
            curr_file = self.ui.cbox_history.currentText()
            user = curr_file.split('-')[-1]
            if CheckResult.load_today_check(user):
                self.check_content = SI.ChecksToday["check_content"]
                CheckResult.load_result()
                self.ui.lineUser.setReadOnly(True)
                self.ui.lineUser.setText(SI.ChecksToday["check_user"])

                self.ui.lineStart.setReadOnly(True)
                local_time = datetime.fromtimestamp(
                    datetime.strptime(SI.ChecksToday["check_date"], '%Y-%m-%d %H:%M:%S').timestamp() - timezone).strftime(
                    '%Y-%m-%d %H:%M:%S')
                self.ui.lineStart.setText(local_time)
                self.update_tree()

                self.execute_flag = True
            else:
                QMessageBox.warning(self.ui, 'Warning', 'There is no execution today. Load Failed.')

    def update_tree(self):
        for item in self.itemlist:
            item_name = item.text(0)
            check = CheckResult.get_check(item_name, SI.ChecksToday)
            self.update_result(item, check["check_result"])
