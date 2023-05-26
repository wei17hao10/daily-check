import re
from PyQt5 import uic
from core.share import SI, CheckItem
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
from core.add_item import AddItem


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
        elif self.type == 'Powershell':
            self.ui.PSBackgroundText.setText(self.background)
            self.ui.te_psScript.setText(self.check[0])
            self.ui.te_checkPSOutput.setText(self.check[1])
            self.ui.te_psOps.setText(self.operations)
        elif self.type == 'Python':
            self.ui.PyBackgroundText.setText(self.background)
            self.ui.te_pyScript.setText(self.check[0])
            self.ui.te_checkPyOutput.setText(self.check[1])
            self.ui.te_pyOps.setText(self.operations)

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
