from PySide import QtGui, QtCore
from models import CDMSVariableListModel


class CDMSVariableList(QtGui.QListView):
    def __init__(self, parent=None):
        super(CDMSVariableList, self).__init__(parent=parent)
        self.setModel(CDMSVariableListModel())
        self.setDragEnabled(True)

    def add_variable(self, cdmsvar):
        self.model().add_variable(cdmsvar)

    def get_variable(self, index):
        return self.model().variables[index]

    def update_variable(self, cdmsvar):
        self.model().update_variable(cdmsvar)
