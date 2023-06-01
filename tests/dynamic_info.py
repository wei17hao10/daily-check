import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Widget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.msgBox = QMessageBox(self)
        self.msgBox.setWindowTitle("Title")
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setText("Start")
        self.msgBox.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimeout)
        self.timer.start(1000)
        print('end')

    def onTimeout(self):
        self.msgBox.setText("datetime: {}".format(QDateTime.currentDateTime().toString()))
        print(format(QDateTime.currentDateTime().toString()))
        if self.timer.isActive():
            print('time is active')
            self.timer.stop()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())