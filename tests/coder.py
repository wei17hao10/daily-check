import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *


class PyMainWindow(QMainWindow):
    def __init__(self):
        super(PyMainWindow, self).__init__()

        # 设置窗口的宽高和标题
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("py功能")
        self.center()

        # 创建一个frame,并设置布局
        self.__frm = QFrame(self)
        self.__frm.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        self.__lvBox = QVBoxLayout()
        self.__frm.setLayout(self.__lvBox)
        self.setCentralWidget(self.__frm)
        # 设置字体
        self.__myFont = QFont()
        # 设置字体大小
        self.__myFont.setPointSize(10)

        # 创建编辑器
        self.__editor = QsciScintilla()
        self.__editor.setText("print('hello word')")
        # self.__editor.append("world")
        self.__editor.setLexer(None)
        self.__editor.setUtf8(True)  # Set encoding to UTF-8
        self.__editor.setFont(self.__myFont)  # Will be overridden by lexer!
        # 添加当前行高亮显示
        self.__editor.setCaretLineVisible(True)  # 是否高亮显示光标所在行
        self.__editor.setCaretLineBackgroundColor(QtGui.QColor('lightblue'))

        # 设置 Tab 键功能
        self.__editor.setIndentationsUseTabs(True)  # 行首缩进采用Tab键，反向缩进是Shift +Tab
        self.__editor.setIndentationWidth(4)  # 行首缩进宽度为4个空格
        self.__editor.setIndentationGuides(True)  # 显示虚线垂直线的方式来指示缩进
        self.__editor.setTabIndents(True)  # 编辑器将行首第一个非空格字符推送到下一个缩进级别
        self.__editor.setAutoIndent(True)  # 插入新行时，自动缩进将光标推送到与前一个相同的缩进级别
        self.__editor.setTabWidth(4)  # Tab 等于 4 个空格
        # 设__editor.置页边特性。 这里有3种Margin：[0]行号 [1]改动标识 [2]代码折叠
        # 设置行号
        self.__editor.setMarginsFont(self.__myFont)  # 行号字体
        self.__editor.setMarginLineNumbers(0, True)  # 设置标号为0的页边显示行号
        self.__editor.setMarginWidth(0, '000')  # 行号宽度
        self.__editor.setMarkerForegroundColor(QColor("#FFFFFF"), 0)

        self.__editor.setEolMode(QsciScintilla.EolUnix)  # 文件中的每一行都以EOL字符结尾（换行符为 \r \n）
        self.__editor.setAutoIndent(True)  # 换行后自动缩进
        self.__editor.setUtf8(True)  # 支持中文字符

        # 设置改动标记
        self.__editor.setMarginType(1, QsciScintilla.SymbolMargin)  # 设置标号为1的页边用于显示改动标记
        self.__editor.setMarginWidth(1, "0000")  # 改动标记占用的宽度

        # 把编辑器添加到布局
        self.__lvBox.addWidget(self.__editor)

        # 添加按钮
        self.__btn = QPushButton("运行指令")
        self.__btn.setFixedWidth(60)
        self.__btn.setFixedHeight(30)
        self.__btn.clicked.connect(self.__btn_action)

        self.__confirm_btn = QPushButton("确认")
        self.__confirm_btn.setFixedWidth(50)
        self.__confirm_btn.setFixedHeight(30)
        self.__confirm_btn.clicked.connect(self.__confirm_btn_action)
        self.__lhBox = QHBoxLayout()
        self.__lhBox.addWidget(self.__btn)
        self.__lhBox.addWidget(self.__confirm_btn)
        self.__lvBox.addLayout(self.__lhBox)
        self.show()

    # 执行py代码
    def __btn_action(self):
        try:
            exec(self.__editor.text())
        except Exception:
            print("运行失败")

    def __confirm_btn_action(self):
        self.code = self.__editor.text()

    # 定义一个函数使得窗口居中显示
    def center(self):
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = PyMainWindow()
    sys.exit(app.exec_())


