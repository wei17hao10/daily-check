import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from core.login import Login
from core.share import SI


def catch_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)

    exception = str("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    QMessageBox.critical(None, 'App crash error', exception)
    SI.logger.error(exception)
    sys.exit(1)


def main():
    app = QApplication(sys.argv)
    sys.excepthook = catch_exception
    app.setWindowIcon(QIcon('./images/logo.png'))
    SI.loadDBCfgFile()
    SI.loadUsersFile()
    # SI.mainWin = Main_window()
    # SI.mainWin.ui.show()
    SI.loginWin = Login()
    SI.loginWin.ui.show()
    # app.exec_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# >> pyinstaller main.py --noconsole --noconfirm --hidden-import pymssql._mssql --icon="logo.ico"
## UI images