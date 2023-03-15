from PyQt5 import uic
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem


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
