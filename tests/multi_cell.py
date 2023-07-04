# mytablewidget.py
import sys

from PyQt5.QtWidgets import QApplication, QMenu, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QTableWidgetItem


class MyTableWidget(QtWidgets.QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 创建QMenu信号事件
        self.customContextMenuRequested.connect(self.showMenu)
        self.contextMenu = QMenu(self)
        self.CP = self.contextMenu.addAction('复制')
        self.JQ = self.contextMenu.addAction('剪切')
        self.NT = self.contextMenu.addAction('粘贴')
        self.CP.triggered.connect(self.copy)
        self.JQ.triggered.connect(self.cut)
        self.NT.triggered.connect(self.paste)

    def del_tb_text(self):
        try:
            indexes = self.selectedIndexes()
            for index in indexes:
                row, column = index.row(), index.column()
                item = QTableWidgetItem()
                self.setItem(row, column, item)
        except BaseException as e:
            print(e)
            return

    def paste_tb_text(self):
        try:
            indexes = self.selectedIndexes()
            for index in indexes:
                index = index
                break
            r, c = index.row(), index.column()
            text = QApplication.clipboard().text()
            ls = text.split('\n')
            ls1 = []
            for row in ls:
                ls1.append(row.split('\t'))
            rows = len(ls)
            columns = len(ls1[0])
            for row in range(rows):
                for column in range(columns):
                    item = QTableWidgetItem()
                    item.setText((str(ls1[row][column])))
                    self.setItem(row + r, column + c, item)
        except Exception as e:
            print(e)
            return

    def selected_tb_text(self):
        try:
            indexes = self.selectedIndexes()  # 获取表格对象中被选中的数据索引列表
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
                    data = self.item(row, column).text()
                    if row_data:
                        row_data = row_data + '\t' + data
                    else:
                        row_data = data

                if text:
                    text = text + '\n' + row_data
                else:
                    text = row_data
            return text
        except BaseException as e:
            print(e)
            return ''

    def copy(self):
        text = self.selected_tb_text()  # 获取当前表格选中的数据
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def cut(self):
        self.copy()
        self.del_tb_text()

    def paste(self):
        self.paste_tb_text()

    def showMenu(self, pos):
        # pos 鼠标位置
        # 菜单显示前,将它移动到鼠标点击的位置
        self.contextMenu.exec_(QCursor.pos())  # 在鼠标位置显示

    def keyPressEvent(self, event):  # 重写键盘监听事件
        # 监听 CTRL+C 组合键，实现复制数据到粘贴板
        if (event.key() == Qt.Key_C) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.copy()  # 获取当前表格选中的数据
        elif (event.key() == Qt.Key_X) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.cut()
        elif (event.key() == Qt.Key_V) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.paste()
        elif (event.key() == Qt.Key_Z) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.paste()
        else:
            super().keyPressEvent(event)


# practice1.py




app = QApplication(sys.argv)
MainWindow = QMainWindow()


class Ui(object):
    def setupUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(737, 677)
        MainWindow.setFixedSize(MainWindow.width(), MainWindow.height())
        self.table = MyTableWidget(MainWindow)
        self.table.setEnabled(True)
        self.table.setGeometry(QtCore.QRect(5, 5, 600, 600))
        self.table.setRowCount(10)
        self.table.setColumnCount(10)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "practice1"))


ui = Ui()
ui.setupUI(MainWindow)
MainWindow.show()
sys.exit(app.exec_())