from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from cdatgui.cdat.models import PlotterListModel
from cdatgui.variables import get_variables


class InspectorWidget(StaticDockWidget):
    plotters_updated = QtCore.Signal(list)

    def __init__(self, spreadsheet, parent=None):
        super(InspectorWidget, self).__init__("Inspector", parent=parent)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.RightDockWidgetArea]
        spreadsheet.selectionChanged.connect(self.selection_change)
        self.cells = []
        self.current_plot = None
        self.plots = PlotterListModel()

        widget = QtGui.QWidget()
        l = QtGui.QVBoxLayout()
        widget.setLayout(l)

        # Plot selector
        label = QtGui.QLabel("Plots:")
        l.addWidget(label)

        plot_combo = QtGui.QComboBox()
        plot_combo.setModel(self.plots)
        plot_combo.currentIndexChanged[int].connect(self.selectPlot)

        l.addWidget(plot_combo)

        self.plot_combo = plot_combo

        l.addWidget(QtGui.QLabel("Variables:"))

        var_combo_1 = QtGui.QComboBox()
        var_combo_1.setModel(get_variables())
        var_combo_1.currentIndexChanged[str].connect(self.setFirstVar)
        var_combo_1.setEnabled(False)

        var_combo_2 = QtGui.QComboBox()
        var_combo_2.setModel(get_variables())
        var_combo_2.currentIndexChanged[str].connect(self.setFirstVar)
        var_combo_2.setEnabled(False)

        self.var_combos = [var_combo_1, var_combo_2]

        for combo in self.var_combos:
            l.addWidget(combo)

        self.setWidget(widget)

    def setFirstVar(self, varId):
        variable = get_variables().get_variable(varId)
        self.current_plot.variables = [variable, self.current_plot.variables[1]]

    def setSecondVar(self, varId):
        variable = get_variables().get_variable(varId)
        self.current_plot.variables = [self.current_plot.variables[0], variable]

    def selectPlot(self, plotIndex):
        if plotIndex < self.plots.rowCount():
            plot = self.plots.get(plotIndex)
            self.current_plot = plot
            # Set the variable combos to the correct indices
            for ind, var in enumerate(plot.variables):
                block = self.var_combos[ind].blockSignals(True)
                if var is None:
                    self.var_combos[ind].setEnabled(False)
                    self.var_combos[ind].setCurrentIndex(-1)
                else:
                    self.var_combos[ind].setEnabled(True)
                    self.var_combos[ind].setCurrentIndex(self.var_combos[ind].findText(var.id))
                self.var_combos[ind].blockSignals(block)
        else:
            for var in self.var_combos:
                block = var.blockSignals(True)
                var.setCurrentIndex(-1)
                var.blockSignals(block)

    def selection_change(self, selected):
        plots = []
        self.cells = []
        self.plots.clear()
        for cell in selected:
            cell = cell.containedWidget
            self.cells.append(cell)
            # cell is now a QCDATWidget
            for plot in cell.getPlotters()[:-1]:
                self.plots.append(plot)
        if self.plots.rowCount() > 0:
            self.plot_combo.setCurrentIndex(0)
