from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from cdatgui.cdat.models import PlotterListModel
from cdatgui.variables import get_variables
from cdatgui.graphics import get_gms
from cdatgui.templates import get_templates
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

        plot_layout = QtGui.QHBoxLayout()

        plot_combo = QtGui.QComboBox()
        plot_combo.setEnabled(False)
        plot_combo.setModel(self.plots)
        plot_combo.currentIndexChanged[int].connect(self.selectPlot)
        plot_layout.addWidget(plot_combo)

        plot_remove = QtGui.QPushButton("Delete")
        plot_remove.clicked.connect(self.deletePlot)
        plot_layout.addWidget(plot_remove)

        l.addLayout(plot_layout)

        self.plot_combo = plot_combo

        l.addWidget(QtGui.QLabel("Variables:"))

        var_1_layout = QtGui.QHBoxLayout()
        var_combo_1 = QtGui.QComboBox()
        var_combo_1.setModel(get_variables())
        var_combo_1.currentIndexChanged[str].connect(self.setFirstVar)
        var_combo_1.setEnabled(False)
        var_1_layout.addWidget(var_combo_1)

        edit_var_1 = QtGui.QPushButton("Edit")
        edit_var_1.clicked.connect(self.editFirstVar)
        var_1_layout.addWidget(edit_var_1)

        var_2_layout = QtGui.QHBoxLayout()
        var_combo_2 = QtGui.QComboBox()
        var_combo_2.setModel(get_variables())
        var_combo_2.currentIndexChanged[str].connect(self.setFirstVar)
        var_combo_2.setEnabled(False)
        var_2_layout.addWidget(var_combo_2)
        edit_var_2 = QtGui.QPushButton("Edit")
        edit_var_2.clicked.connect(self.editSecondVar)
        var_2_layout.addWidget(edit_var_2)

        self.var_combos = [var_combo_1, var_combo_2]

        l.addLayout(var_1_layout)
        l.addLayout(var_2_layout)

        l.addWidget(QtGui.QLabel("Graphics Method:"))


        self.gm_type_combo = QtGui.QComboBox()
        self.gm_type_combo.setModel(get_gms())
        self.gm_type_combo.currentIndexChanged.connect(self.setGMRoot)
        self.gm_type_combo.setEnabled(False)

        l.addWidget(self.gm_type_combo)

        gm_layout = QtGui.QHBoxLayout()

        self.gm_instance_combo = QtGui.QComboBox()
        self.gm_instance_combo.setModel(get_gms())
        self.gm_instance_combo.setRootModelIndex(get_gms().index(0, 0))
        self.gm_instance_combo.setCurrentIndex(0)
        self.gm_instance_combo.setEnabled(False)
        self.gm_instance_combo.currentIndexChanged.connect(self.updateGM)
        gm_layout.addWidget(self.gm_instance_combo)

        edit_gm = QtGui.QPushButton("Edit")
        edit_gm.clicked.connect(self.editGM)
        gm_layout.addWidget(edit_gm)

        l.addLayout(gm_layout)

        l.addWidget(QtGui.QLabel("Template:"))

        template_layout = QtGui.QHBoxLayout()

        self.template_combo = QtGui.QComboBox()
        self.template_combo.setModel(get_templates())
        self.template_combo.setEnabled(False)
        self.template_combo.currentIndexChanged[str].connect(self.setTemplate)
        template_layout.addWidget(self.template_combo)

        edit_templ = QtGui.QPushButton("Edit")
        edit_templ.clicked.connect(self.editTemplate)
        template_layout.addWidget(edit_templ)

        l.addLayout(template_layout)

        self.setWidget(widget)

    def editFirstVar(self):
        pass

    def editSecondVar(self):
        pass

    def editGM(self):
        pass

    def editTemplate(self):
        pass

    def deletePlot(self):
        ind = self.plot_combo.currentIndex()
        plot = self.plots.get(ind)
        self.plots.remove(ind)
        plot.remove()
        self.selectPlot(ind - 1)

    def setGMRoot(self, index):
        self.gm_instance_combo.setRootModelIndex(get_gms().index(index, 0))

    def setTemplate(self, template):
        print template
        self.current_plot.template = vcs.gettemplate(str(template))

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
        if 0 <= plotIndex < self.plots.rowCount():
            self.plot_combo.setEnabled(True)
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
            self.template_combo.setEnabled(True)
            block = self.template_combo.blockSignals(True)
            self.template_combo.setCurrentIndex(self.template_combo.findText(plot.template.name))
            self.template_combo.blockSignals(block)
        else:
            self.plot_combo.setEnabled(False)
            self.gm_type_combo.setEnabled(False)
            self.gm_instance_combo.setEnabled(False)
            self.template_combo.setEnabled(False)
            for v in self.var_combos:
                v.setEnabled(False)

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
        self.plot_combo.setCurrentIndex(0)

