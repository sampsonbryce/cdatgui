from PySide import QtGui, QtCore
from .manager import manager
import os.path
from cdatgui.utils import icon


class CDMSFileItem(QtGui.QTreeWidgetItem):

    def __init__(self, text, parent=None):
        super(CDMSFileItem, self).__init__(parent=parent)
        self.setIcon(0, icon("file.png"))
        self.setText(1, text)
        self.setExpanded(True)
        self.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)


class CDMSFileTree(QtGui.QTreeWidget):

    def __init__(self, parent=None):
        super(CDMSFileTree, self).__init__(parent=parent)
        self.files = {}
        self.setColumnCount(2)
        self.header().close()

    def add_file(self, filepath):
        if filepath in self.files:
            raise ValueError("File '%s' already loaded" % filepath)

        try:
            cdmsfile = manager().get_file(filepath)
        except IOError as e:
            error_dialog = QtGui.QErrorMessage(self)
            error_dialog.showMessage(e.message)
            return

        self.files[filepath] = cdmsfile

        file_name = os.path.basename(cdmsfile.id)

        file_item = CDMSFileItem(file_name)

        for var in cdmsfile.variables:
            var_item = QtGui.QTreeWidgetItem()
            var_item.setText(0, var)
            file_item.addChild(var_item)

        self.addTopLevelItem(file_item)
