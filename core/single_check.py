from PyQt5 import uic
from core.share import SI, ItemMgt, CheckResult
from PyQt5.QtWidgets import QMessageBox
from core.display_result import DisplaySQLResult
import pymssql
import pyperclip as cpb


class SingleCheckResult:
    def __init__(self, current_check, is_hide_pass):
        self.ui = uic.loadUi("UI/further check.ui")
        # self.ui = UI.further_check.Ui_Form()
        # self.widget = MyWidget()
        # self.ui.setupUi(self.widget)

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
        self.is_hide_pass: bool = is_hide_pass

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
        self.ui.btn_close.clicked.connect(self.on_close)
        self.ui.btn_day1ago.clicked.connect(self.click_previous_1)
        self.ui.btn_day2ago.clicked.connect(self.click_previous_2)
        self.ui.btn_day3ago.clicked.connect(self.click_previous_3)
        # self.ui.textComments.textChanged.connect(self.my_close)
        # SI.globalSignal.close_further_check.connect(self.on_close)

        self.load_data()

        # self.widget.show()

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
        # if len(this_comment.strip()) == 0 and today_check["item_type"] == "SQL" and today_check["check_result"][2] == "auto pass":
        #     this_comment = "auto pass"
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
        if len(self.check_sql.strip()) > 0 and self.current_check["item_type"] == 'SQL':
            cpb.copy(self.check_sql)
            QMessageBox.information(self.ui, 'Info', 'SQL is copied.')

    def click_ob(self):
        if len(self.ob_condition.strip()) == 0:
            return
        cpb.copy(self.ob_condition)
        QMessageBox.information(self.ui, 'Info', 'OB condition is copied.')

    def click_jobq(self):
        if len(self.jobq_condition.strip()) == 0:
            return
        cpb.copy(self.jobq_condition)
        QMessageBox.information(self.ui, 'Info', 'jobQ condition is copied.')

    def click_last(self):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.ui, 'Warning', 'Operation Comments can not be empty.')
        else:
            self.update_comment()

            i = self.namelist.index(self.check_name)
            if i - 1 < 0:
                QMessageBox.information(self.ui, 'Info', 'This is the first check item.')
            else:
                current_check = CheckResult.get_check(self.namelist[i-1], SI.ChecksToday)
                self.init_again(current_check)

    def click_next(self):
        this_comment = self.ui.textComments.toPlainText()
        if len(this_comment.strip()) == 0:
            QMessageBox.warning(self.ui, 'Warning', 'Operation Comments can not be empty.')
        else:
            self.update_comment()

            nlistlen = len(self.namelist)
            i = self.namelist.index(self.check_name)

            while True:
                i += 1
                if i < nlistlen:
                    current_check = CheckResult.get_check(self.namelist[i], SI.ChecksToday)
                    if current_check["comment"] == "auto pass" and self.is_hide_pass:
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
                QMessageBox.warning(self.ui, 'Error', 'Connection Error')

    def close_db_conn(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
