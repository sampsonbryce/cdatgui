from PySide import QtGui, QtCore
from cdatgui.variables import get_variables


class CDMSVariableList(QtGui.QListView):

    selected = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(CDMSVariableList, self).__init__(parent=parent)
        self.setModel(get_variables())
        self.setDragEnabled(True)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.activated.connect(self.sel)

    def remove_variable(self, variable):
        if isinstance(variable, int):
            # It's an index
            ind = variable
        else:
            # It's a variable
            for ind, var in enumerate(self.model().variables):
                if var.id == variable.id:
                    break
            else:
                raise ValueError("Variable %s not in Variable List" % (variable.id))
        res = self.model().remove_variable(ind)
        return res

    def add_variable(self, cdmsvar):
        self.model().add_variable(cdmsvar)

    def get_variable(self, index):
        return self.model().get_variable(index)

    def get_variable_label(self, var):
        return self.model().get_variable_label(var)

    def update_variable(self, cdmsvar, label):
        self.model().update_variable(cdmsvar, label)

    def clear(self):
        self.model().clear()

    def sel(self, index):
        i = index.row()
        self.selected.emit(self.get_variable(i))
