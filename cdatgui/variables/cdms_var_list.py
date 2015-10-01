from PySide import QtGui, QtCore
from models import CDMSVariableListModel


class CDMSVariableList(QtGui.QListView):

    selectionChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(CDMSVariableList, self).__init__(parent=parent)
        self.setModel(CDMSVariableListModel())
        self.setDragEnabled(True)
        selection = QtGui.QItemSelectionModel(self.model())
        self.setSelectionModel(selection)
        self.selectionModel().currentChanged.connect(self.changed_selection)

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
        self.model().remove_variable(ind)

    def add_variable(self, cdmsvar):
        self.model().add_variable(cdmsvar)

    def get_variable(self, index):
        return self.model().variables[index]

    def update_variable(self, cdmsvar):
        self.model().update_variable(cdmsvar)

    def clear(self):
        self.model().clear()

    def changed_selection(self, current, previous):
        self.selectionChanged.emit(self.get_variable(current.row()))
