from PyQt5 import uic
from core.share import SI
from core.mainwindow import MainWindow
from PyQt5.QtWidgets import QMessageBox


class Login:
    def __init__(self):
        self.ui = uic.loadUi("UI/login.ui")
        self.ui.loginButton.clicked.connect(self.handle_click)
        # self.ui.loginButton.entered.connect(self.handleclk)

    def handle_click(self):
        luser = self.ui.lineUser.text()
        SI.logger.debug(f'the login user is {luser}')
        userlist = []
        # print('userinfo', SI.userinfo)
        for user in SI.userinfo['Users']:
            userlist.append(user['username'])
        # print('userlist', userlist)
        if luser in userlist:
            SI.user = luser
            self.ui.hide()
            if SI.mainWin is None:
                SI.mainWin = MainWindow()
            else:
                SI.mainWin.put_actions()
            SI.mainWin.ui.show()
        else:
            # print('error username')
            QMessageBox.warning(self.ui, 'Warning', f'User info is not correct.')

        raise ValueError('raise value error test')

