from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from cdatgui.cdat.models import PlotterListModel
from cdatgui.variables import get_variables
from cdatgui.graphics import get_gms
import vcs


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
        plot_combo.setEnabled(False)
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

        l.addWidget(QtGui.QLabel("Graphics Method:"))

        self.gm_type_combo = QtGui.QComboBox()
        self.gm_type_combo.setModel(get_gms())
        self.gm_type_combo.currentIndexChanged.connect(self.setGMRoot)
        self.gm_type_combo.setEnabled(False)
        l.addWidget(self.gm_type_combo)

        self.gm_instance_combo = QtGui.QComboBox()
        self.gm_instance_combo.setModel(get_gms())
        self.gm_instance_combo.setRootModelIndex(get_gms().index(0, 0))
        self.gm_instance_combo.setCurrentIndex(0)
        self.gm_instance_combo.setEnabled(False)
        self.gm_instance_combo.currentIndexChanged.connect(self.updateGM)
        l.addWidget(self.gm_instance_combo)

        self.setWidget(widget)

    def setGMRoot(self, index):
        self.gm_instance_combo.setRootModelIndex(get_gms().index(index, 0))

    def updateGM(self, index):
        gm_type = self.gm_type_combo.currentText()
        gm_name = self.gm_instance_combo.currentText()

        gm = vcs.getgraphicsmethod(gm_type, gm_name)
        self.current_plot.graphics_method = gm

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
            gm = plot.graphics_method
            block = self.gm_instance_combo.blockSignals(True)
            self.gm_type_combo.setCurrentIndex(self.gm_type_combo.findText(vcs.graphicsmethodtype(gm)))
            try:
                self.gm_instance_combo.setCurrentIndex(self.gm_instance_combo.findText(gm.name))
            except:
                pass
            self.gm_instance_combo.blockSignals(block)
            self.gm_instance_combo.setEnabled(True)
            self.gm_type_combo.setEnabled(True)
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
            self.plot_combo.setEnabled(True)
            self.plot_combo.setCurrentIndex(0)
        else:
            self.plot_combo.setEnabled(False)
            self.gm_type_combo.setEnabled(False)
            self.gm_instance_combo.setEnabled(False)
            for v in self.var_combos:
                v.setEnabled(False)
