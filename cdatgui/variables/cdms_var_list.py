from PySide import QtGui


class CDMSVariableList(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(CDMSVariableList, self).__init__(parent=parent)
        self.variables = []

    def add_variable(self, cdmsvar):
        self.variables.append(cdmsvar)
        self.addItem(cdmsvar.id)

    def get_variable(self, index):
        return self.variables[index]
