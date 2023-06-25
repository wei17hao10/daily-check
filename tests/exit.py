import sys
import traceback
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from core.login import Login
from core.share import SI


def handleException(exc_type, exc_value, exc_traceback):
    '''
    使用方法在入口位置,最开始位置(sys.exit(app.exec_())之前 )加入这一行
    sys.excepthook = handle_exception
    类似：import cgitb
        cgitb.enable(format='txt')
    Args:
        exc_type:
        exc_value:
        exc_traceback:

    Returns:

    '''
    if issubclass(exc_type, KeyboardInterrupt):
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)

    exception = str("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    dialog = QtWidgets.QDialog()
    # close对其进行删除操作
    dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    msg = QtWidgets.QMessageBox(dialog)
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText('程序异常,请联系管理员!')
    msg.setWindowTitle("系统异常提示")
    msg.setDetailedText(exception)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

    msg.exec_()


def main():
    r = None

    try:
        app = QtWidgets.QApplication(sys.argv)
        sys.excepthook = handleException
        # import cgitb
        # cgitb.enable(format='txt')

        win = LoginWindow()
        win.show()
        r = app.exec_()
        print("app exec:", r)
    except:
        traceback.print_exc()
    sys.exit(r)
