from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from uiClass import Login
from lib.share import SI


if __name__ == '__main__':
    app = QApplication([])
    app.setWindowIcon(QIcon('./images/logo.png'))
    SI.loadDBCfgFile()
    SI.loadUsersFile()
    # SI.mainWin = Main_window()
    # SI.mainWin.ui.show()
    SI.loginWin = Login()
    SI.loginWin.ui.show()
    app.exec_()

# >> pyinstaller main.py --noconsole --noconfirm --hidden-import pymssql._mssql --icon="logo.ico"
