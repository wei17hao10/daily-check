from PyQt5 import uic
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem
from core.share import SI
import pyperclip as cpb


class DisplaySQLResult:
    def __init__(self, fields, rows):
        self.ui = uic.loadUi("./UI/sqlresult.ui")
        self.fields = fields
        self.rows = rows
        self.set_content()
        self.ui.btn_copy.clicked.connect(self.selected_tb_text)

    def set_content(self):
        fieldlen = len(self.fields)
        rowlen = len(self.rows)
        table_widget = self.ui.tableSQLResult
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_widget.setColumnCount(fieldlen)
        if rowlen >= 500:
            rowlen = 500
            self.rows = self.rows[:500]
        table_widget.setRowCount(rowlen)
        table_widget.setHorizontalHeaderLabels(self.fields)
        for i, row in enumerate(self.rows):
            for j in range(len(self.fields)):
                new_item = QTableWidgetItem(str(row[j]))
                table_widget.setItem(i, j, new_item)

    def selected_tb_text(self):
        table_widget = self.ui.tableSQLResult
        try:
            indexes = table_widget.selectedIndexes()  # 获取表格对象中被选中的数据索引列表
            indexes_dict = {}
            for index in indexes:  # 遍历每个单元格
                row, column = index.row(), index.column()  # 获取单元格的行号，列号
                if row in indexes_dict.keys():
                    indexes_dict[row].append(column)
                else:
                    indexes_dict[row] = [column]

            # 将数据表数据用制表符(\t)和换行符(\n)连接，使其可以复制到excel文件中
            text = ''
            for row, columns in indexes_dict.items():
                row_data = ''
                for column in columns:
                    data = table_widget.item(row, column).text()
                    if row_data:
                        row_data = row_data + '\t' + data
                    else:
                        row_data = data

                if text:
                    text = text + '\n' + row_data
                else:
                    text = row_data
            cpb.copy(text)
        except Exception as e:
            SI.logger.warning(e)
            cpb.copy('')
