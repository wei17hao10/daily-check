import re
from PyQt5 import uic
from core.share import SI, ItemMgt
from core.add_item import AddItem
from core.modify_item import ModifyItem
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QHeaderView
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt


class CheckItemConfig:
    def __init__(self):
        self.ui = uic.loadUi("UI/itemconfwidget.ui")
        self.headerName = {}
        self.get_header_map()

        self.load_item_info()
        # self.ui.actionAdd_Item.triggered.connect(self.load_add_item)
        # self.ui.actionModify_Item.triggered.connect(self.modify_item)
        # self.ui.actionDelete_Item.triggered.connect(self.deleteItem)
        # self.ui.actionDeactivate_Item.triggered.connect(self.deactivateItem)
        # self.ui.actionActivate_Item.triggered.connect(self.activateItem)

        self.ui.btn_Add.clicked.connect(self.load_add_item)
        self.ui.btn_Edit.clicked.connect(self.modify_item)
        self.ui.btn_Delete.clicked.connect(self.delete_item)
        self.ui.btn_Deactivate.clicked.connect(self.deactivate_item)
        self.ui.btn_Activate.clicked.connect(self.activate_item)
        self.ui.btn_Refresh.clicked.connect(self.refresh_display)
        self.ui.itemTree.itemDoubleClicked.connect(self.set_sort_editable)
        self.ui.itemTree.itemChanged.connect(self.sort_changed)

        # self.ms = MySignals()
        # self.ms.update_item_config.connect(self.load_item_info)
        SI.globalSignal.update_item_config.connect(self.load_item_info)
        self.additem = None
        self.mItem = None

    def get_header_map(self):
        ColCount = self.ui.itemTree.headerItem().columnCount()
        num2name = {}
        for i in range(ColCount):
            num2name[str(i)] = self.ui.itemTree.headerItem().text(i)
        self.headerName = {num2name[key]: int(key) for key in num2name.keys()}
        # {
        # 'Item Name': 0,
        # 'Sort Order': 1,
        # 'Created By': 2,
        # 'Created Date': 3,
        # 'Updated By': 4,
        # 'Updated Date': 5
        # }

    def set_sort_editable(self, item, col):
        if col == self.headerName['Sort Order']:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        else:
            item.setFlags(item.flags() & ~ Qt.ItemIsEditable)

    def sort_changed(self, tree_item, col):
        if col == self.headerName['Sort Order']:
            curritem = ItemMgt.get_item(tree_item.text(self.headerName['Item Name']))
            sorder = tree_item.text(col)
            pattern = '^[1-9]$'
            res = re.fullmatch(pattern, sorder)
            if res is None:
                QMessageBox.warning(self.ui, 'Warning', 'Number should between 1~9.')
                tree_item.setText(col, curritem.sortOrder)
            else:
                curritem.sortOrder = sorder
                curritem.save_check_item()

    def refresh_display(self):
        ItemMgt.update_itemdf()
        self.load_item_info()

    def load_item_info(self):
        self.ui.itemTree.clear()
        self.load_item_type('Manual')
        self.load_item_type('Powershell')
        self.load_item_type('Python')
        self.load_item_type('SQL')

        self.ui.itemTree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def load_item_type(self, itemtype):
        items = SI.itemDF[SI.itemDF['type'] == itemtype].values
        tree = self.ui.itemTree
        root = tree.invisibleRootItem()
        folderItem = QTreeWidgetItem()
        folderIcon = QIcon("../images/folder.png")
        # 设置节点图标
        folderItem.setIcon(self.headerName['Item Name'], folderIcon)
        # 设置该节点  第1个column 文本
        folderItem.setText(self.headerName['Item Name'], itemtype)
        # 添加到树的不可见根节点下，就成为第一层节点
        root.addChild(folderItem)
        # 设置该节点为展开状态
        folderItem.setExpanded(True)
        for item in items:
            leafItem = QTreeWidgetItem()
            folderItem.addChild(leafItem)
            leafItem.setText(self.headerName['Item Name'], item[2])
            leafItem.setText(self.headerName['Created By'], item[4])
            leafItem.setTextAlignment(self.headerName['Created By'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Created Date'], item[5])
            leafItem.setTextAlignment(self.headerName['Created Date'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Updated By'], item[6])
            leafItem.setTextAlignment(self.headerName['Updated By'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Updated Date'], item[7])
            leafItem.setTextAlignment(self.headerName['Updated Date'], Qt.AlignVCenter | Qt.AlignHCenter)
            leafItem.setText(self.headerName['Sort Order'], str(item[8]))
            leafItem.setTextAlignment(self.headerName['Sort Order'], Qt.AlignVCenter | Qt.AlignHCenter)

            if item[3] == 'active':
                leafIcon = QIcon("../images/active item.png")
                leafItem.setIcon(self.headerName['Item Name'], leafIcon)
                leafItem.setForeground(self.headerName['Item Name'], QColor('black'))
            elif item[3] == 'inactive':
                leafIcon = QIcon("../images/deactived item.png")
                leafItem.setIcon(self.headerName['Item Name'], leafIcon)
                leafItem.setForeground(self.headerName['Item Name'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Created By'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Created Date'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Updated By'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Updated Date'], QColor(180, 180, 180))
                leafItem.setForeground(self.headerName['Sort Order'], QColor(180, 180, 180))
            else:
                leafItem.setForeground(self.headerName['Item Name'], QColor(220, 220, 220))

    def load_add_item(self):
        self.additem = AddItem()
        self.additem.ui.show()

    def modify_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)

            self.mItem = ModifyItem(curritem)
            self.mItem.ui.show()

    def delete_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)

            ItemMgt.delete_item(curritem)
            self.load_item_info()

    def deactivate_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)
            if curritem.status == 'active':
                curritem.status = 'inactive'
                curritem.save_check_item()
                ItemMgt.update_itemdf()
                # set icon and color
                leafIcon = QIcon("../images/deactived item.png")
                currentItem.setIcon(self.headerName['Item Name'], leafIcon)
                currentItem.setForeground(self.headerName['Item Name'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Created By'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Created Date'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Updated By'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Updated Date'], QColor(180, 180, 180))
                currentItem.setForeground(self.headerName['Sort Order'], QColor(180, 180, 180))

            elif curritem.status == 'inactive':
                QMessageBox.information(self.ui, 'Info', 'The item is already inactive')

    def activate_item(self):
        tree = self.ui.itemTree
        currentItem = tree.currentItem()
        if not currentItem:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        elif currentItem.text(self.headerName['Item Name']) in SI.ITEM_TYPE:
            QMessageBox.warning(self.ui, 'Warning', 'Please choose an item.')
        else:
            itemname = currentItem.text(self.headerName['Item Name'])
            curritem = ItemMgt.get_item(itemname)
            if curritem.status == 'inactive':
                curritem.status = 'active'
                curritem.save_check_item()
                ItemMgt.update_itemdf()
                # set icon and color
                leafIcon = QIcon("../images/active item.png")
                currentItem.setIcon(self.headerName['Item Name'], leafIcon)
                currentItem.setForeground(self.headerName['Item Name'], QColor('black'))
                currentItem.setForeground(self.headerName['Created By'], QColor('black'))
                currentItem.setForeground(self.headerName['Created Date'], QColor('black'))
                currentItem.setForeground(self.headerName['Updated By'], QColor('black'))
                currentItem.setForeground(self.headerName['Updated Date'], QColor('black'))
                currentItem.setForeground(self.headerName['Sort Order'], QColor('black'))

            elif curritem.status == 'active':
                QMessageBox.information(self.ui, 'Info', 'The item is already active')
