from PySide import QtGui, QtCore
from cdatgui.variables.cdms_var_list import CDMSVariableList
from cdatgui.variables.models import CDMSVariableListModel
from cdatgui.variables import get_variables


class VariableInspector(QtGui.QWidget):
    variableUpdated = QtCore.Signal(object)
    variableListUpdated = QtCore.Signal(list)
    currentChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(VariableInspector, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.plots = []
        self.var_list = CDMSVariableList()
        model = CDMSVariableListModel()
        self.var_list.setModel(model)

        layout.addWidget(self.var_list)
        self.variableListUpdated.connect(self.updateVarList)
        self.var_list.selected.connect(self.setCurrentVar)
        self.current_var = None

    def setCurrentVar(self, var):
        self.current_var = var
        self.currentChanged.emit(self.current_var)

    def updateVarList(self, vars):
        self.var_list.clear()
        all_vars = get_variables()
        for v in vars:
            self.var_list.add_variable(all_vars.get_variable(v.id))

    def setPlots(self, plots):
        variables = []
        for plot in plots:
            v = plot.variables
            if v:
                for var in v:
                    if var is not None:
                        variables.append(var)
        self.plots = plots
        self.variableListUpdated.emit(variables)
