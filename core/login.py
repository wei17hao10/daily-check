from PyQt5 import uic
from core.share import SI
from core.mainwindow import MainWindow
from PyQt5.QtWidgets import QMessageBox


class Login:
    def __init__(self):
        self.ui = uic.loadUi("UI/login.ui")
        self.ui.loginButton.clicked.connect(self.handle_click)

    def handle_click(self):
        luser = self.ui.lineUser.text()
        # SI.logger.debug(f'the login user is {luser}')
        userlist = []
        for user in SI.userinfo['Users']:
            userlist.append(user['username'])
        if luser in userlist:
            SI.user = luser
            self.ui.hide()
            if SI.mainWin is None:
                SI.mainWin = MainWindow()
            else:
                SI.mainWin.put_actions()
            SI.mainWin.ui.show()
        else:
            QMessageBox.warning(self.ui, 'Warning', f'User info is not correct.')

