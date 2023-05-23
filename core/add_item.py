import re
from PyQt5 import uic
from core.share import SI, ItemMgt
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
import pymssql
from core.display_result import DisplaySQLResult
from core.powershell import PowerShell


class AddItem:
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
        self.ui.btn_exeps.clicked.connect(self.execute_ps)
        self.ui.btn_checkpsres.clicked.connect(self.check_ps_result)

    def execute_ps(self):
        pass

    def check_ps_result(self):
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
