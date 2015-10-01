from PySide import QtGui, QtCore
from cdatgui.variables.cdms_var_list import CDMSVariableList


class VariableInspector(QtGui.QWidget):
    variablesUpdated = QtCore.Signal(list)
    currentChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(VariableInspector, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.plots = []
        self.var_list = CDMSVariableList()
        layout.addWidget(self.var_list)
        self.variablesUpdated.connect(self.updateVarList)
        self.current_var = None

    def setCurrentVar(self, var):
        self.current_var = var
        self.currentChanged.emit(self.current_var)

    def updateVarList(self, vars):
        self.var_list.clear()
        for v in vars:
            self.var_list.add_variable(v)

    def setPlots(self, plots):
        variables = []
        for plot in plots:
            v = plot.variables
            for var in v:
                if var is not None:
                    variables.append(var)
        self.plots = plots
        self.variablesUpdated.emit(variables)
