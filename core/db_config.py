from PyQt5 import uic
from core.share import SI
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import json
import pymssql
from PyQt5.QtCore import Qt


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
        with open('conf/dbcfg.json', 'w+', encoding='utf8') as f:
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
