import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class HoverLabelExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Hover Label Example')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # 创建一个标签
        self.label = QLabel('悬停我', self)
        layout.addWidget(self.label)

        # 为标签设置一个提示信息
        self.label.setToolTip('这是悬停信息')

        # 连接鼠标悬停和鼠标离开事件到处理函数
        self.label.mousePressEvent = self.onMousePress
        # self.label.mouseReleaseEvent = self.onMouseRelease

        self.setLayout(layout)

    def onMousePress(self, event):
        # 鼠标悬停时显示提示信息
        self.label.setToolTip('这是悬停信息')

    def onMouseRelease(self, event):
        # 鼠标离开时清除提示信息
        self.label.setToolTip('')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HoverLabelExample()
    ex.show()
    sys.exit(app.exec_())
