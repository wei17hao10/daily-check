from threading import Thread

from PyQt5 import uic
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtCore import Qt
from core.share import SI, ItemMgt
from core.user_config import UserConfig
from core.db_config import DBConfig
from core.check_item_config import CheckItemConfig
from core.check_all_result import CheckAllResult
from core.python_editor import PythonEditor


class MainWindow:
    def __init__(self):
        if SI.user == '':
            SI.user = 'admin'
        self.ui = uic.loadUi("UI/mainwin.ui")
        self.ui.actionUser_Config.triggered.connect(self.open_user_config)
        self.ui.actionDB_Config.triggered.connect(self.open_db_config)
        self.ui.actionCheck_Item_Config.triggered.connect(self.open_check_item_config)
        self.ui.actionExit.triggered.connect(self.exit_main)
        self.ui.actionExecute_all.triggered.connect(self.execute_all)
        self.ui.actionPythonEditor.triggered.connect(self.open_python_editor)

        self.put_actions()

        ItemMgt.load_all_items()

    def put_actions(self):
        # print(SI.user)
        priv_exe = 2
        priv_conf = 0
        for user in SI.userinfo["Users"]:
            if SI.user == user["username"]:
                priv_exe = user["execution"]
                priv_conf = user["configuration"]
                break

        self.switch_action(priv_conf, self.ui.actionUser_Config)
        self.switch_action(priv_conf, self.ui.actionDB_Config)
        self.switch_action(priv_conf, self.ui.actionCheck_Item_Config)
        self.switch_action(priv_conf, self.ui.actionPythonEditor)
        self.switch_action(priv_exe, self.ui.actionExecute_all)
        self.switch_action(2, self.ui.actionExit)

    def switch_action(self, priv, action):
        if priv == 0:
            self.ui.menu.removeAction(action)
            self.ui.toolBar.removeAction(action)
        elif priv == 2:
            self.ui.menu.addAction(action)
            self.ui.toolBar.addAction(action)

    def _open_sub_window(self, FuncClass):
        def create_sub_window():
            subWin = QMdiSubWindow()
            # subWin.setWindowTitle(str(FuncClass.__name__))
            funcCase = FuncClass()
            subWin.setWidget(funcCase.ui)
            subWin.setAttribute(Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(subWin)
            # 这里添加funcCase共享的原因是：如果不添加，这个实例就会在函数执行完成后被销毁，这样cellchanged信号就找不到回调函数了。
            # 添加subWin共享的原因是，要调用其show函数
            SI.subWinTable[str(FuncClass)] = {'subWin': subWin, 'funcCase': funcCase}
            subWin.show()
            subWin.setWindowState(Qt.WindowActive | Qt.WindowMaximized)

        if str(FuncClass) not in SI.subWinTable:
            create_sub_window()
            return

        subWin = SI.subWinTable[str(FuncClass)]['subWin']
        try:
            subWin.show()
            subWin.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
        except:
            create_sub_window()

    def open_db_config(self):
        self._open_sub_window(DBConfig)

    def open_check_item_config(self):
        self._open_sub_window(CheckItemConfig)

    def open_user_config(self):
        self._open_sub_window(UserConfig)

    def exit_main(self):
        self.ui.close()
        SI.loginWin.ui.lineUser.setText('')
        SI.subWinTable = {}
        SI.mainWin = None
        SI.loginWin.ui.show()

    def execute_all(self):
        self._open_sub_window(CheckAllResult)

    def open_python_editor(self):
        self._open_sub_window(PythonEditor)
        # t = Thread(target=self._open_sub_window, kwargs={"FuncClass": PythonEditor})
        # t.start()
