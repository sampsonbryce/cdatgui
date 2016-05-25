from PySide import QtGui, QtCore
from functools import partial

from cdatgui.cdat.importer import import_script
from cdatgui.cdat.exporter import export_script
from cdatgui.variables.manager import manager
import os
from cdatgui.variables.manipulations.manipulation import Manipulations


class MainMenu(QtGui.QMenuBar):
    def __init__(self, spreadsheet, var, gm, tmpl, parent=None):
        super(MainMenu, self).__init__(parent=parent)

        self.ss = spreadsheet
        self.var = var
        self.gm = gm
        self.tmpl = tmpl
        self.manipulations = Manipulations()

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
        seasonal_climatology.triggered.connect(partial(self.manipulations.launchClimatologyDialog, 'seasonal'))

        monthly_climatology = self.edit_data_menu.addAction("Monthly Climatologies")
        monthly_climatology.triggered.connect(partial(self.manipulations.launchClimatologyDialog, 'monthly'))

        regrid = self.edit_data_menu.addAction("Regrid")
        regrid.triggered.connect(self.manipulations.launchRegridDialog)

        average = self.edit_data_menu.addAction("Average")
        average.triggered.connect(self.manipulations.launchAverageDialog)

        summation = self.edit_data_menu.addAction("Summation")
        summation.triggered.connect(self.manipulations.launchSumDialog)

        std = self.edit_data_menu.addAction("Standard Deviation")
        std.triggered.connect(self.manipulations.launchSTDDialog)

        departure = self.edit_data_menu.addAction("Departures")
        departure.triggered.connect(self.manipulations.launchDepartureDialog)

        correlation = self.edit_data_menu.addAction("Correlation")
        correlation.triggered.connect(
            partial(self.manipulations.launchCorrelationOrCovarianceDialog, correlation.text()))

        covariance = self.edit_data_menu.addAction("Covariance")
        covariance.triggered.connect(partial(self.manipulations.launchCorrelationOrCovarianceDialog, covariance.text()))

        lagged_correlation = self.edit_data_menu.addAction("Lagged Correlation")
        lagged_correlation.triggered.connect(
            partial(self.manipulations.launchCorrelationOrCovarianceDialog, lagged_correlation.text()))

        lagged_covariance = self.edit_data_menu.addAction("Lagged Covariance")
        lagged_covariance.triggered.connect(
            partial(self.manipulations.launchCorrelationOrCovarianceDialog, lagged_covariance.text()))

        linear_regression = self.edit_data_menu.addAction("Linear Regression")
        linear_regression.triggered.connect(self.manipulations.launchLinearRegressionDialog)

        geometric_mean = self.edit_data_menu.addAction("Geometric Mean")
        geometric_mean.triggered.connect(self.manipulations.launchGeometricMeanDialog)

        weighted_mean = self.edit_data_menu.addAction("Weighted Mean")

        variance = self.edit_data_menu.addAction("Variance")
        variance.triggered.connect(self.manipulations.launchVarianceDialog)

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
