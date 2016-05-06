from PySide import QtGui, QtCore
import os.path
from collections import OrderedDict

from cdatgui.utils import icon
import urlparse

clickcount = 0
label_font = None
label_icon_size = None
label_icon = None


class CDMSFileItem(QtGui.QTreeWidgetItem):

    def __init__(self, text, uri, parent=None):
        global label_font, label_icon_size, label_icon

        if label_font is None:
            label_font = QtGui.QFont()
            label_font.setBold(True)
            label_icon_size = QtCore.QSize(16, 16)
            label_icon = icon("bluefile.png")

        super(CDMSFileItem, self).__init__(parent=parent)

        self.uri = uri
        self.setSizeHint(0, label_icon_size)
        self.setIcon(0, label_icon)
        self.setText(1, text)
        self.setFont(1, label_font)
        self.setExpanded(True)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)


class CDMSFileTree(QtGui.QTreeWidget):

    def __init__(self, parent=None):
        super(CDMSFileTree, self).__init__(parent=parent)
        self.files = {}
        self.files_ordered = []
        self.setColumnCount(2)
        self.setSelectionMode(CDMSFileTree.ExtendedSelection)
        self.header().resizeSection(0, 48)
        self.header().close()

    def add_file(self, cdmsfile):
        if cdmsfile.uri in self.files:
            return

        self.files[cdmsfile.uri] = cdmsfile

        self.files_ordered.append(cdmsfile)

        parsed = urlparse.urlparse(cdmsfile.uri)

        file_name = os.path.basename(parsed.path)

        file_item = CDMSFileItem(file_name, cdmsfile.uri)

        for var in cdmsfile.variables:
            var_item = QtGui.QTreeWidgetItem()
            var_item.setText(1, var)
            file_item.addChild(var_item)

        self.addTopLevelItem(file_item)
        file_item.setExpanded(True)

    def get_selected(self):
        items = self.selectedItems()
        variables = OrderedDict()
        for item in items:
            new_vars = []
            if isinstance(item, CDMSFileItem):
                for index in range(item.childCount()):
                    new_vars.append(item.child(index))
            else:
                new_vars.append(item)
            for var in new_vars:
                var_name = var.text(1)
                file_index = self.indexOfTopLevelItem(var.parent())
                cdmsfile = self.files_ordered[file_index]
                var_meta_item = cdmsfile(var_name)
                if var.text(1) not in variables.values():
                    variables[var_meta_item] = var.text(1)

        return variables.keys()
