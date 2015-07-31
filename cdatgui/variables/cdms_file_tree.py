from PySide import QtGui, QtCore
import os.path
from cdatgui.utils import icon

clickcount = 0
label_font = None
label_icon_size = None
label_icon = None


class CDMSFileItem(QtGui.QTreeWidgetItem):

    def __init__(self, text, parent=None):
        global label_font, label_icon_size, label_icon

        if label_font is None:
            label_font = QtGui.QFont()
            label_font.setBold(True)
            label_icon_size = QtCore.QSize(16, 16)
            label_icon = icon("bluefile.png")

        super(CDMSFileItem, self).__init__(parent=parent)
        self.setSizeHint(0, label_icon_size)
        self.setIcon(0, label_icon)
        self.setText(1, text)
        self.setFont(1, label_font)
        self.setExpanded(True)
        self.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)


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
        if cdmsfile.id in self.files:
            raise ValueError("File '%s' already loaded" % cdmsfile.id)

        self.files[cdmsfile.id] = cdmsfile

        self.files_ordered.append(cdmsfile)

        file_name = os.path.basename(cdmsfile.id)

        file_item = CDMSFileItem(file_name)

        for var in cdmsfile.variables:
            var_item = QtGui.QTreeWidgetItem()
            var_item.setText(1, var)
            file_item.addChild(var_item)

        self.addTopLevelItem(file_item)
        file_item.setExpanded(True)

    def get_selected(self):
        items = self.selectedItems()
        variables = []
        for item in items:
            var_name = item.text(1)
            file_index = self.indexOfTopLevelItem(item.parent())
            cdmsfile = self.files_ordered[file_index]
            variables.append(cdmsfile(var_name))

        return variables
