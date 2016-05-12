from PySide import QtGui, QtCore
from functools import partial

from cdatgui.bases.input_dialog import AccessableButtonDialog, ValidatingInputDialog
from cdatgui.cdat.importer import import_script
from cdatgui.cdat.exporter import export_script
from cdatgui.utils import label
from cdatgui.variables import get_variables
from cdatgui.variables.manager import manager
import os
import cdutil
import numpy

from cdatgui.variables.variable_add import FileNameValidator


class ClimatologyDialog(AccessableButtonDialog):
    def __init__(self, climo_type, parent=None):
        super(ClimatologyDialog, self).__init__(parent=parent)

        self.climo_combo = QtGui.QComboBox()
        if climo_type == 'seasonal':
            self.climo_combo.addItems(['DJF', 'MAM', 'JJA', 'SON', 'YEAR'])
        else:
            self.climo_combo.addItems(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])

        clim_label = label("Climatology:")

        clim_layout = QtGui.QHBoxLayout()
        clim_layout.addWidget(clim_label)
        clim_layout.addWidget(self.climo_combo)

        self.variable_combo = QtGui.QComboBox()
        self.variable_combo.setModel(get_variables())

        variable_label = label("Variable:")

        variable_layout = QtGui.QHBoxLayout()
        variable_layout.addWidget(variable_label)
        variable_layout.addWidget(self.variable_combo)

        self.vertical_layout.insertLayout(0, clim_layout)
        self.vertical_layout.insertLayout(1, variable_layout)

        if climo_type == 'seasonal':
            self.bounds_combo = QtGui.QComboBox()
            self.bounds_combo.addItems(['Daily', 'Monthly', 'Yearly'])

            bounds_label = label('Bounds:')

            bounds_layout = QtGui.QHBoxLayout()
            bounds_layout.addWidget(bounds_label)
            bounds_layout.addWidget(self.bounds_combo)

            self.vertical_layout.insertLayout(2, bounds_layout)

        self.save_button.setText('Save as')

    def getClimatology(self):
        return self.climo_combo.currentText()

    def getVar(self):
        return self.variable_combo.currentText()

    def getBounds(self):
        return self.bounds_combo.currentText()

    def accept(self):
        self.accepted.emit()


class MainMenu(QtGui.QMenuBar):
    def __init__(self, spreadsheet, var, gm, tmpl, parent=None):
        super(MainMenu, self).__init__(parent=parent)

        self.ss = spreadsheet
        self.var = var
        self.gm = gm
        self.tmpl = tmpl
        self.dialog = None
        self.name_dialog = None

        file_menu = self.addMenu("File")
        openscript = file_menu.addAction("Open Script")
        openscript.setShortcut(QtGui.QKeySequence.Open)
        openscript.triggered.connect(self.open_script)

        save = file_menu.addAction("Save Script")
        save.setShortcut(QtGui.QKeySequence.Save)
        save.triggered.connect(self.save_script)

        self.edit_data_menu = self.addMenu("Edit Data")
        self.edit_data_menu.setEnabled(False)
        seasonal_climatology = self.edit_data_menu.addAction("Seasonal Climatologies")
        seasonal_climatology.triggered.connect(partial(self.createClimatology, 'seasonal'))

        monthly_climatology = self.edit_data_menu.addAction("Monthly Climatologies")
        monthly_climatology.triggered.connect(partial(self.createClimatology, 'month'))

        regrid = self.edit_data_menu.addAction("Regrid")

        Average = self.edit_data_menu.addAction("Average")

    def createClimatology(self, ctype):
        self.dialog = ClimatologyDialog(ctype)
        self.dialog.accepted.connect(partial(self.getName, ctype))
        self.dialog.rejected.connect(self.dialog.deleteLater)
        self.dialog.setMinimumSize(300, 200)
        self.dialog.show()
        self.dialog.raise_()

    def getName(self, ctype):
        self.name_dialog = ValidatingInputDialog()
        self.name_dialog.setValidator(FileNameValidator())
        self.name_dialog.setWindowTitle("Save As")
        self.name_dialog.setLabelText('Enter New Name:')
        if ctype == 'seasonal':
            text = '{0}_{1}_{2}_climatology'.format(self.dialog.getClimatology(), self.dialog.getBounds().lower(), self.dialog.getVar())
        else:
            text = '{0}_{1}_climatology'.format(self.dialog.getClimatology(), self.dialog.getVar())

        count = 1
        while get_variables().variable_exists(text):
            if count == 1:
                text = text + '_' + str(count)
            else:
                text = text[:-2] + '_' + str(count)
            count += 1

        self.name_dialog.setTextValue(text)

        self.name_dialog.edit.selectAll()
        self.name_dialog.accepted.connect(self.makeClimatologyVar)
        self.name_dialog.rejected.connect(self.name_dialog.deleteLater)
        self.name_dialog.show()
        self.name_dialog.raise_()

    def makeClimatologyVar(self):
        climo = self.dialog.getClimatology()
        var_name = self.dialog.getVar()
        var = get_variables().get_variable(var_name)
        var = var.var

        if climo in ['DJF', 'MAM', 'JJA', 'SON', 'ANN']:
            bounds = self.dialog.getBounds()
            time_axis = var.getTime()
            if bounds == "Daily":
                cdutil.setAxisTimeBoundsDaily(time_axis)
            elif bounds == "Monthly":
                cdutil.setAxisTimeBoundsMonthly(time_axis)
            elif bounds == "Yearly":
                cdutil.setAxisTimeBoundsYearly(time_axis)
            else:
                raise ValueError("No bounds function for %s" % bounds)
        else:
            time_axis = var.getTime()
            cdutil.setAxisTimeBoundsMonthly(time_axis)

        if climo == "DJF":
            new_var = cdutil.DJF.climatology(var)
        elif climo == "MAM":
            new_var = cdutil.MAM.climatology(var)
        elif climo == "JJA":
            new_var = cdutil.JJA.climatology(var)
        elif climo == "SON":
            new_var = cdutil.SON.climatology(var)
        elif climo == "YEAR":
            new_var = cdutil.YEAR.climatology(var)
        elif climo == 'JAN':
            new_var = cdutil.JAN.climatology(var)
        elif climo == 'FEB':
            new_var = cdutil.FEB.climatology(var)
        elif climo == 'MAR':
            new_var = cdutil.MAR.climatology(var)
        elif climo == 'APR':
            new_var = cdutil.APR.climatology(var)
        elif climo == 'MAY':
            new_var = cdutil.MAY.climatology(var)
        elif climo == 'JUN':
            new_var = cdutil.JUN.climatology(var)
        elif climo == 'JUL':
            new_var = cdutil.JUL.climatology(var)
        elif climo == 'AUG':
            new_var = cdutil.AUG.climatology(var)
        elif climo == 'SEP':
            new_var = cdutil.SEP.climatology(var)
        elif climo == 'OCT':
            new_var = cdutil.OCT.climatology(var)
        elif climo == 'NOV':
            new_var = cdutil.NOV.climatology(var)
        elif climo == 'DEC':
            new_var = cdutil.DEC.climatology(var)

        new_var.id = self.name_dialog.textValue()
        get_variables().add_variable(new_var)

        # cleanup
        self.dialog.close()
        self.dialog.deleteLater()

        self.name_dialog.close()
        self.name_dialog.deleteLater()

    def open_script(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self,
                                                     u"Open Script",
                                                     "/",
                                                     u"CDAT Scripts (*.py)"
                                                     )
        if filePath[0] == u"":
            return
        if os.path.exists(filePath[0]) is False:
            return

        script = import_script(filePath[0])

        self.var.load(script.variables.values())

        rows, cols = script.rows, script.columns
        num_canvases = script.num_canvases

        cells = self.ss.load(rows, cols, num_canvases)

        canvases = [cell.canvas for cell in cells]
        displays = script.plot(canvases)

        # Now we need to sync up the plotters with the displays
        for cell, display_plots in zip(cells, displays):
            cell.load(display_plots)
            # TODO:
            # Should also load graphics methods and templates into
            # appropriate widgets if they're named

    def save_script(self):
        filePath = QtGui.QFileDialog.getSaveFileName(self, u"Save Script", "/",
                                                     u"CDAT Scripts (*.py)")

        rows, columns = self.ss.getRowsAndColumns()
        cells = []
        plotters = []
        for r in range(rows):
            for c in range(columns):
                cell = self.ss.getCell(r, c)
                cells.append(cell)
                plotters.append(cell.getPlotters()[:-1])

        var_manager = manager()
        all_files = var_manager.files.values()
        all_variables = {}
        for f in all_files:
            for var in f.vars:
                all_variables[var.data_key()] = var

        used_variables = []
        # Now that we have all variables sorted out, let's grab relevant ones
        for pgroup in plotters:
            for plotter in pgroup:
                if plotter.can_plot() is False:
                    continue
                for v in plotter.variables:
                    if v is None:
                        continue
                    v_key = v.id

                    if v_key in all_variables:
                        used_variables.append(all_variables[v_key])
                        del all_variables[v_key]

        export_script(filePath[0], used_variables, plotters,
                      rows=rows, columns=columns)
