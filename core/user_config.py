from PyQt5 import uic
from core.share import SI
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QInputDialog, QLineEdit
from datetime import datetime
import json


class UserConfig:
    def __init__(self):
        self.ui = uic.loadUi("UI/adduser.ui")
        self.users = SI.userinfo['Users']
        self.item2data = {}
        self.load_user_to_tree()

        self.ui.btn_AddUser.clicked.connect(self.add_user)
        self.ui.btn_DelUser.clicked.connect(self.delete_user)
        self.ui.userTree.itemChanged.connect(self.update_user)

    def update_user(self, item, col):
        username = item.text(0)
        user = self.item2data[username]
        if col == 2:
            user['execution'] = item.checkState(col)
        elif col == 3:
            user['configuration'] = item.checkState(col)
        self.save_user_to_file()

    def load_user_to_tree(self):
        tree = self.ui.userTree
        tree.clear()
        self.item2data = {}
        root = tree.invisibleRootItem()
        for user in self.users:
            userItem = QTreeWidgetItem()
            userItem.setText(0, user['username'])
            userItem.setText(1, user['joindate'])
            userItem.setCheckState(2, user['execution'])
            userItem.setCheckState(3, user['configuration'])
            root.addChild(userItem)
            userItem.setExpanded(True)
            self.item2data[user['username']] = user

    def save_user_to_file(self):
        userinfo = {'Users': self.users,
                    'UpdateDate': datetime.now().strftime('%Y-%m-%d')
                    }
        SI.userinfo = userinfo
        with open('conf/users.json', 'w+', encoding='utf8') as f:
            json.dump(userinfo, f, indent=4)

    def add_user(self):
        # print('add user')
        username, okPressed = QInputDialog.getText(self.ui, "Input Info", "New Username:", QLineEdit.Normal, "")
        # print('username:', username)
        if okPressed:
            # print('OK clicked')
            user = {"username": username,
                    "joindate": datetime.now().strftime('%Y-%m-%d'),
                    "execution": 2,
                    "configuration": 0
                    }
            self.users.append(user)
            self.save_user_to_file()
            self.load_user_to_tree()

    def delete_user(self):
        currItem = self.ui.userTree.currentItem()
        if currItem is None:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            username = currItem.text(0)
            choice = QMessageBox.question(self.ui, 'Confirmation', f'Are you sure you want to delete this user: {username}?')
            if choice == QMessageBox.Yes:
                user = self.item2data[username]
                idx = self.users.index(user)
                self.users.pop(idx)
                self.save_user_to_file()
                self.load_user_to_tree()
