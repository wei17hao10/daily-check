from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from core.login import Login
from core.share import SI


def main():
    app = QApplication([])
    app.setWindowIcon(QIcon('./images/logo.png'))
    SI.loadDBCfgFile()
    SI.loadUsersFile()
    # SI.mainWin = Main_window()
    # SI.mainWin.ui.show()
    SI.loginWin = Login()
    SI.loginWin.ui.show()
    app.exec_()


if __name__ == '__main__':
    main()

# >> pyinstaller main.py --noconfirm --hidden-import pymssql._mssql --icon="logo.ico"
# >> pyinstaller main.py --noconsole --noconfirm --hidden-import pymssql._mssql --icon="logo.ico"
## UI images