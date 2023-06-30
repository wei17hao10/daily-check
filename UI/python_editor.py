from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtGui import QColor, QFont


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(632, 506)
        Form.setStyleSheet("font: 9pt \"Titillium Web\";")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalGroupBox = QtWidgets.QGroupBox(Form)
        self.verticalGroupBox.setObjectName("verticalGroupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalGroupBox)
        self.verticalLayout.setObjectName("verticalLayout")

######################################
        # self.te_python = QtWidgets.QTextEdit(self.verticalGroupBox)
        # self.te_python.setStyleSheet("font: 11pt \"Titillium Web\";")
        # self.te_python.setObjectName("te_python")
        # self.verticalLayout.addWidget(self.te_python)

        self.te_python = QsciScintilla(self.verticalGroupBox)
        self.te_python.setStyleSheet("font: 11pt \"Titillium Web\";")
        self.te_python.setObjectName("te_python")
        self.verticalLayout.addWidget(self.te_python)

        self.te_python.setText("print('hello word')")
        lexer = QsciLexerPython()
        self.te_python.setLexer(lexer)
        self.te_python.setUtf8(True)  # Set encoding to UTF-8
        self._font = QFont()
        self._font.setPointSize(10)
        self.te_python.setFont(self._font)  # Will be overridden by lexer!
        # 添加当前行高亮显示
        self.te_python.setCaretLineVisible(True)  # 是否高亮显示光标所在行
        self.te_python.setCaretLineBackgroundColor(QtGui.QColor('lightblue'))
        # 设置 Tab 键功能
        self.te_python.setIndentationsUseTabs(True)  # 行首缩进采用Tab键，反向缩进是Shift +Tab
        self.te_python.setIndentationWidth(4)  # 行首缩进宽度为4个空格
        self.te_python.setIndentationGuides(True)  # 显示虚线垂直线的方式来指示缩进
        self.te_python.setTabIndents(True)  # 编辑器将行首第一个非空格字符推送到下一个缩进级别
        self.te_python.setAutoIndent(True)  # 插入新行时，自动缩进将光标推送到与前一个相同的缩进级别
        self.te_python.setTabWidth(4)  # Tab 等于 4 个空格
        # 设__editor.置页边特性。 这里有3种Margin：[0]行号 [1]改动标识 [2]代码折叠
        # 设置行号
        self.te_python.setMarginsFont(self._font)  # 行号字体
        self.te_python.setMarginLineNumbers(0, True)  # 设置标号为0的页边显示行号
        self.te_python.setMarginWidth(0, '000')  # 行号宽度
        self.te_python.setMarkerForegroundColor(QColor("#FFFFFF"), 0)
        self.te_python.setEolMode(QsciScintilla.EolUnix)  # 文件中的每一行都以EOL字符结尾（换行符为 \r \n）
        self.te_python.setAutoIndent(True)  # 换行后自动缩进
        self.te_python.setUtf8(True)  # 支持中文字符
        # 设置改动标记
        self.te_python.setMarginType(1, QsciScintilla.SymbolMargin)  # 设置标号为1的页边用于显示改动标记
        self.te_python.setMarginWidth(1, "0000")  # 改动标记占用的宽度
######################################

        self.btn_execute = QtWidgets.QPushButton(self.verticalGroupBox)
        self.btn_execute.setObjectName("btn_execute")
        self.verticalLayout.addWidget(self.btn_execute)
        self.horizontalLayout.addWidget(self.verticalGroupBox)
        self.verticalGroupBox1 = QtWidgets.QGroupBox(Form)
        self.verticalGroupBox1.setObjectName("verticalGroupBox1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalGroupBox1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tb_result = QtWidgets.QTextBrowser(self.verticalGroupBox1)
        self.tb_result.setStyleSheet("font: 11pt \"Titillium Web\";")
        self.tb_result.setObjectName("tb_result")
        self.verticalLayout_2.addWidget(self.tb_result)
        self.horizontalLayout.addWidget(self.verticalGroupBox1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.verticalGroupBox.setTitle(_translate("Form", "Python script editor"))
        self.btn_execute.setText(_translate("Form", "Execute"))
        self.verticalGroupBox1.setTitle(_translate("Form", "Result display"))
