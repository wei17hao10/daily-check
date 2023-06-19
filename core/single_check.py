from PyQt5 import uic
from core.share import SI, ItemMgt, CheckResult
from PyQt5.QtWidgets import QMessageBox
from core.display_result import DisplaySQLResult
import pymssql
import pyperclip as cpb
from PyQt5.QtCore import QTimer, Qt
from core.powershell import PowerShell
from runpy import run_path
import os


class SingleCheckResult:
    def __init__(self, current_check, is_hide_pass):
        self.ui = uic.loadUi("UI/further check.ui")
        # self.ui = UI.further_check.Ui_Form()
        # self.widget = MyWidget()
        # self.ui.setupUi(self.widget)

        self.current_check = current_check
        self.conn = None
        self.check_cmd = ''
        self.ob_condition = ''
        self.jobq_condition = ''
        self.fields = []
        self.rows = []
        self.day1comment = ''
        self.day2comment = ''
        self.day3comment = ''
        self.check_name = self.current_check["check_name"]
        self.item_type = self.current_check["item_type"]
        self.single_exe_flag = False
        self.is_hide_pass: bool = is_hide_pass

        self.timer_interval = 3000
        self.sql_timer = QTimer()
        self.sql_timer.timeout.connect(self.on_sqltimer_timeout)

        self.ob_timer = QTimer()
        self.ob_timer.timeout.connect(self.on_obtimer_timeout)

        self.jq_timer = QTimer()
        self.jq_timer.timeout.connect(self.on_jqtimer_timeout)

        self.namelist = [item[2] for item in SI.itemDF[SI.itemDF['status'] == 'active'].values]
        self.btn_style = {
            "grey":     '''QPushButton{color:rgb(180,180,180);font-size:11px;}''',
            "black":    '''QPushButton{color:rgb(30,30,30);font-size:11px;}''',
            "blue":     '''QPushButton{color: #4a86e8;font-size:14px;}'''
        }
        # self.grey_style = '''QPushButton{color:rgb(180,180,180);}'''
        self.ui.btn_check.clicked.connect(self.execute)
        self.ui.btn_result.clicked.connect(self.show_result)
        self.ui.btn_SQL.clicked.connect(self.click_sql)
        self.ui.btn_ob.clicked.connect(self.click_ob)
        self.ui.btn_jobq.clicked.connect(self.click_jobq)
        self.ui.btn_last.clicked.connect(self.click_last)
        self.ui.btn_next.clicked.connect(self.click_next)
        self.ui.btn_close.clicked.connect(self.on_close)
        self.ui.btn_day1ago.clicked.connect(self.click_previous_1)
        self.ui.btn_day2ago.clicked.connect(self.click_previous_2)
        self.ui.btn_day3ago.clicked.connect(self.click_previous_3)
        self.ui.btn_cpcomment.clicked.connect(self.copy_comment)
        self.ui.btn_clrformat.clicked.connect(self.clear_format)
        self.text_format = self.ui.textComments.currentCharFormat()
        # print(self.text_format)
        # self.ui.textComments.textChanged.connect(self.my_close)
        # SI.globalSignal.close_further_check.connect(self.on_close)

        self.load_data()

        # self.widget.show()

    def init_again(self, current_check):
        self.current_check = current_check
        # self.conn = None
        self.check_cmd = ''
        self.ob_condition = ''
        self.jobq_condition = ''
        self.fields = []
        self.rows = []
        self.day1comment = ''
        self.day2comment = ''
        self.day3comment = ''
        self.check_name = self.current_check["check_name"]
        self.item_type = self.current_check["item_type"]
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
        self.check_cmd = item.check[0]
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

        if len(self.check_cmd.strip()) > 0 and item.type == 'SQL':
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

        if SI.Checks1Day != {}:
            day1check = CheckResult.get_check(self.check_name, SI.Checks1Day)
            if day1check is not None:
                self.day1comment = '--[no COMMENT this day]--' if day1check["comment"] == '' else day1check["comment"]
            else:
                self.day1comment = '--[no CHECK this day]--'
        else:
            self.day1comment = '--[no CHECK this day]--'

        if SI.Checks2Day != {}:
            day2check = CheckResult.get_check(self.check_name, SI.Checks2Day)
            if day2check is not None:
                self.day2comment = '--[no COMMENT this day]--' if day2check["comment"] == '' else day2check["comment"]
            else:
                self.day2comment = '--[no CHECK this day]--'
        else:
            self.day2comment = '--[no CHECK this day]--'

        if SI.Checks3Day != {}:
            day3check = CheckResult.get_check(self.check_name, SI.Checks3Day)
            if day3check is not None:
                self.day3comment = '--[no COMMENT this day]--' if day3check["comment"] == '' else day3check["comment"]
            else:
                self.day3comment = '--[no CHECK this day]--'
        else:
            self.day3comment = '--[no CHECK this day]--'

        self.click_previous_1()

    def execute(self):
        if self.item_type == 'SQL':
            self.execute_sql()
        elif self.item_type == 'Powershell':
            self.execute_ps()
        elif self.item_type == 'Python':
            self.execute_py()
        else:
            pass

    def execute_py(self):
        script_dir = 'Checks/pyscripts/execute'
        script_file = self.check_name + '.py'
        script_path = os.path.join(script_dir, script_file)

        msg_box = QMessageBox(self.ui)
        msg_box.setWindowTitle("Executing...")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("The python script is executing, please wait.")
        msg_box.show()

        try:
            result = run_path(path_name=script_path)
        except:
            # QMessageBox.warning(self.ui, 'warning', 'Script execution failed, please check!')
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText('Script execution failed, please check!')
            return

        if 'output' in result:
            if isinstance(result['output'], str):
                output = result['output']
                msg_box.setWindowTitle("Result")
                msg_box.setText(output)
            else:
                # QMessageBox.warning(self.ui, 'warning', 'isPass is not boolean!')
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText('output is not string, please check!')
        else:
            # QMessageBox.warning(self.ui, 'warning', 'isPass is not defined!')
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText('output is not defined, please check!')

    def execute_ps(self):
        msg_box = QMessageBox(self.ui)
        msg_box.setWindowTitle("Executing...")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("The powershell script is executing, please wait.")
        msg_box.show()

        with PowerShell() as ps:
            outs, errs = ps.run(self.check_cmd)
        outs = str(outs)
        errs = str(errs)
        output = 'Output:\n' + outs + '\nErrors:\n' + errs

        msg_box.setWindowTitle("Result")
        msg_box.setText(output)
        msg_box.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def execute_sql(self):
        if self.single_exe_flag:
            return

        self.create_db_conn()
        cursor = self.conn.cursor()
        self.single_exe_flag = True
        self.update_btn_color()
        try:
            cursor.execute(self.check_cmd)
            self.fields = [field[0] for field in cursor.description]
            self.rows = cursor.fetchall()
        except pymssql.ProgrammingError:
            QMessageBox.warning(self.ui, 'Warning', 'Programming Error, please check the SQL.')
        except pymssql.Error:
            QMessageBox.warning(self.ui, 'Warning', 'General Error')
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
        if len(self.check_cmd.strip()) == 0 or self.current_check["item_type"] != 'SQL':
            return
        cpb.copy(self.check_cmd)
        # QMessageBox.information(self.ui, 'Info', 'SQL is copied.')
        if self.sql_timer.isActive():
            self.sql_timer.stop()

        self.ui.btn_SQL.setText("SQL copied")
        self.sql_timer.start(self.timer_interval)

    def on_sqltimer_timeout(self):
        if self.sql_timer.isActive():
            self.sql_timer.stop()
        self.ui.btn_SQL.setText("SQL")

    def click_ob(self):
        if len(self.ob_condition.strip()) == 0:
            return
        cpb.copy(self.ob_condition)
        # QMessageBox.information(self.ui, 'Info', 'OB condition is copied.')
        if self.ob_timer.isActive():
            self.ob_timer.stop()

        self.ui.btn_ob.setText("OB condition copied")
        self.ob_timer.start(self.timer_interval)

    def on_obtimer_timeout(self):
        if self.ob_timer.isActive():
            self.ob_timer.stop()
        self.ui.btn_ob.setText("OB condition")

    def click_jobq(self):
        if len(self.jobq_condition.strip()) == 0:
            return
        cpb.copy(self.jobq_condition)
        # QMessageBox.information(self.ui, 'Info', 'jobQ condition is copied.')
        if self.jq_timer.isActive():
            self.jq_timer.stop()

        self.ui.btn_jobq.setText("JobQ condition copied")
        self.jq_timer.start(self.timer_interval)

    def on_jqtimer_timeout(self):
        if self.jq_timer.isActive():
            self.jq_timer.stop()
        self.ui.btn_jobq.setText("JobQ condition")

    def click_last(self):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.ui, 'Warning', 'Operation Comments can not be empty.')
        else:
            self.update_comment()

            i = self.namelist.index(self.check_name)

            while True:
                i -= 1
                if i < 0:
                    QMessageBox.information(self.ui, 'Info', 'This is the first check item.')
                    break
                else:
                    current_check = CheckResult.get_check(self.namelist[i], SI.ChecksToday)
                    if current_check["check_result"][2] == "auto pass" and self.is_hide_pass:
                        continue
                    self.init_again(current_check)
                    break

    def click_next(self):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.ui, 'Warning', 'Operation Comments can not be empty.')
        else:
            self.update_comment()
            SI.globalSignal.update_check_all.emit(self.current_check)

            nlistlen = len(self.namelist)
            i = self.namelist.index(self.check_name)

            while True:
                i += 1
                if i < nlistlen:
                    current_check = CheckResult.get_check(self.namelist[i], SI.ChecksToday)
                    if current_check["check_result"][2] == "auto pass" and self.is_hide_pass:
                        continue
                    self.init_again(current_check)
                    break
                else:
                    QMessageBox.information(self.ui, 'Info', 'This is the last check item.')
                    break

    def on_close(self):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.ui, 'Warning', 'Operation Comments can not be empty.')
        else:
            self.update_comment()
            self.close_db_conn()
            CheckResult.save_result()
            self.ui.close()
            SI.globalSignal.update_check_all.emit(self.current_check)
            SI.mainWin.ui.hide()
            SI.mainWin.ui.show()

    def update_comment(self):
        today_check = CheckResult.get_check(self.check_name, SI.ChecksToday)
        this_comment = self.ui.textComments.toPlainText()
        if today_check["comment"] != this_comment:
            today_check["comment"] = this_comment

        final = "Operation Done" if self.ui.radioOpDone.isChecked() else "No Operation"
        today_check["check_result"][2] = final

    def click_previous_1(self):
        self.ui.btn_day1ago.setStyleSheet(self.btn_style["blue"])
        self.ui.btn_day2ago.setStyleSheet(self.btn_style["black"])
        self.ui.btn_day3ago.setStyleSheet(self.btn_style["black"])
        self.ui.textPreComment.setText(self.day1comment)

    def click_previous_2(self):
        self.ui.btn_day1ago.setStyleSheet(self.btn_style["black"])
        self.ui.btn_day2ago.setStyleSheet(self.btn_style["blue"])
        self.ui.btn_day3ago.setStyleSheet(self.btn_style["black"])
        self.ui.textPreComment.setText(self.day2comment)

    def click_previous_3(self):
        self.ui.btn_day1ago.setStyleSheet(self.btn_style["black"])
        self.ui.btn_day2ago.setStyleSheet(self.btn_style["black"])
        self.ui.btn_day3ago.setStyleSheet(self.btn_style["blue"])
        self.ui.textPreComment.setText(self.day3comment)

    def copy_comment(self):
        comment = self.ui.textPreComment.toPlainText()
        self.ui.textComments.setText(comment)

    def clear_format(self):
        comment = self.ui.textComments.toPlainText()
        self.ui.textComments.setCurrentCharFormat(self.text_format)
        self.ui.textComments.setPlainText(comment)

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
