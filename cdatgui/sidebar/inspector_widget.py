from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from cdatgui.cdat.models import PlotterListModel
from cdatgui.variables import get_variables
from cdatgui.graphics import get_gms
from cdatgui.templates import get_templates
from cdatgui.variables.edit_variable_widget import EditVariableDialog
from cdatgui.templates.dialog import TemplateEditorDialog
from cdatgui.graphics.dialog import BoxfillDialog
import vcs


class ComboButton(QtGui.QWidget):
    clicked_button = QtCore.Signal(object)
    selected_object = QtCore.Signal(object)

    def __init__(self, model, button_text, parent=None):
        super(ComboButton, self).__init__(parent=parent)
        self.model = model

        layout = QtGui.QHBoxLayout()

        self.combo = QtGui.QComboBox()
        self.combo.setModel(model)
        self.combo.currentIndexChanged.connect(self.select)
        layout.addWidget(self.combo, 1)

        self.button = QtGui.QPushButton(button_text)
        self.button.clicked.connect(self.click)
        layout.addWidget(self.button, 0)

        self.setLayout(layout)

    def setEnabled(self, en):
        self.combo.setEnabled(en)
        self.button.setEnabled(en)

    def currentObj(self):
        ind = self.combo.currentIndex()
        return self.model.get(ind)

    def currentIndex(self):
        return self.combo.currentIndex()

    def setCurrentIndex(self, ind):
        self.combo.setCurrentIndex(ind)

    def findText(self, txt):
        return self.combo.findText(txt)

    def click(self):
        self.clicked_button.emit(self.currentObj())

    def select(self, ind):
        if self.model.rowCount() > 0 and ind >= 0:
            self.selected_object.emit(self.currentObj())
        else:
            self.selected_object.emit(None)


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

        plots = ComboButton(self.plots, "Delete")
        plots.selected_object.connect(self.selectPlot)
        plots.clicked_button.connect(self.deletePlot)
        l.addWidget(plots)
        self.plot_combo = plots

        l.addWidget(QtGui.QLabel("Variables:"))

        var_1 = ComboButton(get_variables(), "Edit")
        var_1.selected_object.connect(self.setFirstVar)
        var_1.clicked_button.connect(self.editFirstVar)
        l.addWidget(var_1)

        var_2 = ComboButton(get_variables(), "Edit")
        var_2.selected_object.connect(self.setSecondVar)
        var_2.clicked_button.connect(self.editSecondVar)
        l.addWidget(var_2)

        self.var_combos = [var_1, var_2]

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
        gm_layout.addWidget(self.gm_instance_combo, 1)

        edit_gm = QtGui.QPushButton("Edit")
        edit_gm.clicked.connect(self.editGM)
        gm_layout.addWidget(edit_gm, 0)
        self.edit_gm_button = edit_gm
        edit_gm.setEnabled(False)
        l.addLayout(gm_layout)

        l.addWidget(QtGui.QLabel("Template:"))

        self.template_combo = ComboButton(get_templates(), "Edit")
        self.template_combo.selected_object.connect(self.setTemplate)
        self.template_combo.clicked_button.connect(self.editTemplate)
        l.addWidget(self.template_combo)

        self.plot_combo.setEnabled(False)
        for v in self.var_combos:
            v.setEnabled(False)
        self.template_combo.setEnabled(False)

        self.tmpl_editor = None
        self.var_editor = None
        self.current_var = None
        self.gm_editor = None
        self.setWidget(widget)

    def editVar(self, var):
        get_variables().update_variable(var, var.id)

    def makeVar(self, var):
        get_variables().add_variable(var)
        combo = self.var_combos[self.current_var]
        # Use the new variable
        combo.setCurrentIndex(get_variables().rowCount() - 1)

    def editVariable(self, var):
        if self.var_editor:
            self.var_editor.reject()
            self.var_editor.deleteLater()
        self.var_editor = EditVariableDialog(var)
        self.var_editor.createdVariable.connect(self.makeVar)
        self.var_editor.editedVariable.connect(self.editVar)
        self.var_editor.show()
        self.var_editor.raise_()

    def editFirstVar(self, var):
        self.current_var = 0
        self.editVariable(var)

    def editSecondVar(self, var):
        self.current_var = 1
        self.editVariable(var)

    def editGraphicsMethod(self, gm):
        get_gms().replace(get_gms().indexOf("boxfill", gm), gm)
        self.current_plot.graphics_method = gm

    def makeGraphicsMethod(self, gm):
        get_gms().add_gm(gm)
        self.gm_instance_combo.setCurrentIndex(self.gm_instance_combo.count() - 1)
        self.current_plot.graphics_method = gm

    def editGM(self):
        gm_type = self.gm_type_combo.currentText()
        gm_name = self.gm_instance_combo.currentText()

        gm = vcs.getgraphicsmethod(gm_type, gm_name)
        if self.gm_editor:
            self.gm_editor.reject()
            self.gm_editor.deleteLater()
        self.gm_editor = BoxfillDialog(gm, self.var_combos[0].currentObj(), self.template_combo.currentObj())
        self.gm_editor.createdGM.connect(self.makeGraphicsMethod)
        self.gm_editor.editedGM.connect(self.editGraphicsMethod)
        self.gm_editor.show()
        self.gm_editor.raise_()

    def makeTmpl(self, template):
        get_templates().add_template(template)

    def editTmpl(self, template):
        ind = get_templates().indexOf(template)
        if ind.isValid():
            get_templates.replace(ind.row(), template)

    def editTemplate(self, tmpl):
        if self.tmpl_editor:
            self.tmpl_editor.reject()
            self.tmpl_editor.deleteLater()
        self.tmpl_editor = TemplateEditorDialog(tmpl)
        self.tmpl_editor.createdTemplate.connect(self.makeTmpl)
        self.tmpl_editor.editedTemplate.connect(self.editTmpl)
        self.tmpl_editor.show()
        self.tmpl_editor.raise_()

    def deletePlot(self, plot):
        ind = self.plot_combo.currentIndex()
        self.plots.remove(ind)
        plot.remove()

    def setGMRoot(self, index):
        self.gm_instance_combo.setRootModelIndex(get_gms().index(index, 0))

    def setTemplate(self, template):
        self.current_plot.template = template

    def updateGM(self, index):
        gm_type = self.gm_type_combo.currentText()
        gm_name = self.gm_instance_combo.currentText()

        gm = vcs.getgraphicsmethod(gm_type, gm_name)
        self.current_plot.graphics_method = gm

    def setFirstVar(self, var):
        self.current_plot.variables = [var, self.current_plot.variables[1]]

    def setSecondVar(self, var):
        self.current_plot.variables = [self.current_plot.variables[0], var]

    def selectPlot(self, plot):
        plotIndex = self.plot_combo.currentIndex()
        if 0 <= plotIndex < self.plots.rowCount():
            self.plot_combo.setEnabled(True)
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
            if self.gm_type_combo.currentText() == "boxfill":
                self.edit_gm_button.setEnabled(True)
            else:
                self.edit_gm_button.setEnabled(False)
        else:
            self.plot_combo.setEnabled(False)
            self.gm_type_combo.setEnabled(False)
            self.gm_instance_combo.setEnabled(False)
            self.template_combo.setEnabled(False)
            self.edit_gm_button.setEnabled(False)
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
