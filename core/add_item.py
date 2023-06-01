import re
import os
from PyQt5 import uic
from core.share import SI, ItemMgt
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
import pymssql
from core.display_result import DisplaySQLResult
from core.powershell import PowerShell
from runpy import run_path


class AddItem:
    def __init__(self):
        self.ui = uic.loadUi("./UI/additemwidget.ui")
        self.background = ''
        self.check = ['', '']
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
        self.output = ''

        # self.ui.lineThreshold.setText(self.check[1])
        self.ui.itemTypeCombo.addItems(SI.ITEM_TYPE)
        self.ui.itemTypeCombo.currentIndexChanged.connect(self.handle_selection_change)
        self.ui.lineThreshold.setText('0')

        self.ui.btn_OK.clicked.connect(self.ok_clicked)
        self.ui.btn_cancel.clicked.connect(self.cancel_clicked)
        self.ui.btn_execute.clicked.connect(self.execute_sql)
        self.ui.btn_checksqlres.clicked.connect(self.display_result)
        self.ui.btn_exeps.clicked.connect(self.execute_ps)
        self.ui.btn_checkpsout.clicked.connect(self.check_result)
        self.ui.btn_exepy.clicked.connect(self.execute_py)
        self.ui.btn_checkpyout.clicked.connect(self.check_result)

    def execute_ps(self):
        msgBox = QMessageBox(self.ui)
        msgBox.setWindowTitle("Executing...")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("The powershell script is executing, please wait.")
        msgBox.show()

        ps_cmd = self.ui.te_psScript.toPlainText()
        # print(ps_cmd)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run(ps_cmd)
        outs = str(outs)
        errs = str(errs)
        self.output = 'Output:\n' + outs + '\nErrors:\n' + errs

        msgBox.setWindowTitle("Result")
        msgBox.setText(self.output)

    def check_result(self):
        if len(self.output.strip()) == 0:
            QMessageBox.warning(self.ui, 'Warning', 'No output, please execute script first.')
            return

        self.save_check_script()
        script_dir = 'Checks/pyscripts/check_result'
        script_file = self.itemname + '.py'
        script_path = os.path.join(script_dir, script_file)
        result = {}

        if os.path.exists(script_path):
            check_params = {'output': self.output}
            try:
                result = run_path(path_name=script_path, init_globals=check_params)
            except:
                QMessageBox.warning(self.ui, 'warning', 'Script execution failed, please check!')
            if 'isPass' in result:
                if isinstance(result['isPass'], bool):
                    info = 'Result: isPass = ' + str(result['isPass'])
                    QMessageBox.information(self.ui, 'Info', info)
                else:
                    QMessageBox.warning(self.ui, 'warning', 'isPass is not boolean!')
            else:
                QMessageBox.warning(self.ui, 'warning', 'isPass is not defined!')
        else:
            QMessageBox.information(self.ui, 'Info', 'The check output script is not defined')

    def execute_py(self):
        pass

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
            self.obcondition = self.ui.OBText.toPlainText()
            self.jbqcondition = self.ui.JBQText.toPlainText()
            # print('after ops')
            if len(self.background.strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input background info.')
                return False
            elif len(self.check[0].strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input SQL.')
                return False
            elif not self.check[1].isdigit():
                QMessageBox.warning(self.ui, 'Warning', 'Threshold is not a number.')
                return False
            elif len(self.operations.strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input Operations steps when check failed.')
                return False
            else:
                # print('true')
                return True
        elif self.type == 'Manual':
            self.background = self.ui.MBackgroundText.toPlainText()
            self.check[0] = self.ui.MCheckProcessText.toPlainText()
            self.operations = self.ui.MOpsText.toPlainText()
            if len(self.background.strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input background info.')
                return False
            elif len(self.check[0].strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input manual check process.')
                return False
            elif len(self.operations.strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input Operations steps when check failed.')
                return False
            else:
                return True
        elif self.type == 'Powershell':
            self.background = self.ui.PSBackgroundText.toPlainText()
            self.check[0] = self.ui.te_psScript.toPlainText()
            self.check[1] = self.ui.te_checkPSOutput.toPlainText()
            self.operations = self.ui.te_psOps.toPlainText()
            # print('after ops')
            if len(self.background.strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input background info.')
                return False
            elif len(self.check[0].strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please Powershell script.')
                return False
            elif len(self.operations.strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input Operations steps when check failed.')
                return False
            else:
                return True
        elif self.type == 'Python':
            self.background = self.ui.PyBackgroundText.toPlainText()
            self.check[0] = self.ui.te_pyScript.toPlainText()
            self.check[1] = self.ui.te_checkPyOutput.toPlainText()
            self.operations = self.ui.te_pyOps.toPlainText()
            # print('after ops')
            if len(self.background.strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please input background info.')
                return False
            elif len(self.check[0].strip()) == 0:
                QMessageBox.warning(self.ui, 'Warning', 'Please Python script.')
                return False
            elif len(self.operations.strip()) == 0:
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
        self.save_check_script()

    def save_check_script(self):
        script = self.check[1]
        script_dir = 'Checks/pyscripts/check_result'
        script_file = self.itemname + '.py'
        script_path = os.path.join(script_dir, script_file)

        def save_script():
            s_file = open(script_path, 'w')
            s_file.write(script)
            s_file.close()

        if os.path.exists(script_path):
            file = open(script_path, 'r')
            file_read = file.read()
            file.close()
            if file_read != script and len(script.strip()) > 0:
                save_script()
            elif len(script.strip()) == 0:
                os.remove(script_path)
        else:
            if len(script.strip()) > 0:
                save_script()

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
