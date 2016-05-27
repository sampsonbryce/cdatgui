import re
from PySide import QtGui, QtCore
from functools import partial

from cdatgui.bases.input_dialog import AccessibleButtonDialog
from cdatgui.cdat.importer import import_script
from cdatgui.cdat.exporter import export_script
from cdatgui.utils import label
from cdatgui.variables import get_variables
from cdatgui.variables.manager import manager
import os, cdms2
from cdatgui.variables.manipulations.manipulation import Manipulations, SelectionChangedListWidget

file_extensions = ['nc', 'cdg', 'NC', 'CDF', 'nc4', 'NC4']


class FileNameValidator(QtGui.QValidator):
    validInput = QtCore.Signal()
    invalidInput = QtCore.Signal()

    def validate(self, inp, pos):
        period_ind = inp.rfind('.')
        if self.isValidName(inp) and (period_ind != len(inp) - 1 and (period_ind == -1 or (
                        period_ind != -1 and inp[period_ind + 1:] in file_extensions))):
            self.validInput.emit()
            return QtGui.QValidator.Acceptable
        else:

            self.invalidInput.emit()
            return QtGui.QValidator.Intermediate

    def isValidName(self, name):
        return not (
            not re.search("^[a-zA-Z_]", name) or name == '' or re.search(' +', name) or re.search("[^a-zA-Z0-9_.]+",
                                                                                                  name))


class FilePathValidator(QtGui.QValidator):
    validInput = QtCore.Signal()
    invalidInput = QtCore.Signal()

    def validate(self, inp, pos):
        if os.path.exists(inp):
            self.validInput.emit()
            return QtGui.QValidator.Acceptable
        else:
            self.invalidInput.emit()
            return QtGui.QValidator.Intermediate


class FilenameAndPathDialog(AccessibleButtonDialog):
    def __init__(self, parent=None):
        super(FilenameAndPathDialog, self).__init__(parent=parent)
        self.dialog = None
        self.file_name_edit = QtGui.QLineEdit()

        validator = FileNameValidator()
        validator.invalidInput.connect(self.update)
        validator.validInput.connect(self.update)
        self.file_name_edit.setValidator(validator)
        self.save_button.setEnabled(False)

        self.file_path_edit = QtGui.QLineEdit()
        validator = FilePathValidator()
        validator.invalidInput.connect(self.update)
        validator.validInput.connect(self.update)
        self.file_path_edit.setValidator(validator)
        self.file_path_edit.setText('/')
        file_browser_button = QtGui.QPushButton('Browse')
        file_browser_button.clicked.connect(self.launchFileBrowser)
        file_path_layout = QtGui.QHBoxLayout()
        file_path_layout.addWidget(self.file_path_edit)
        file_path_layout.addWidget(file_browser_button)

        label_layout = QtGui.QVBoxLayout()
        label_layout.addWidget(label('Path:'))
        label_layout.addWidget(label('Filename:'))

        line_edit_layout = QtGui.QVBoxLayout()
        line_edit_layout.addWidget(self.file_name_edit)
        line_edit_layout.addLayout(file_path_layout)

        edits_layout = QtGui.QHBoxLayout()
        edits_layout.addLayout(label_layout)
        edits_layout.addLayout(line_edit_layout)

        self.vertical_layout.insertLayout(0, edits_layout)

        self.setMinimumSize(300, 300)

        self.update()

    def launchFileBrowser(self):
        self.dialog = QtGui.QFileDialog(directory='/')
        self.dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.dialog.setFileMode(QtGui.QFileDialog.Directory)
        self.dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        self.dialog.accepted.connect(self.updatePath)
        self.dialog.exec_()
        self.dialog.raise_()

    def updatePath(self):
        file_path = self.dialog.selectedFiles()[0]
        self.file_path_edit.setText(file_path)
        self.file_path_edit.validator().validate(file_path, 0)

    def update(self):
        validator = self.file_path_edit.validator()
        block = validator.blockSignals(True)
        if validator.validate(self.file_path_edit.text(), 0) == QtGui.QValidator.Intermediate:
            self.save_button.setEnabled(False)
            validator.blockSignals(block)
            return
        else:
            self.save_button.setEnabled(True)
        validator.blockSignals(block)

        validator = self.file_name_edit.validator()
        block = validator.blockSignals(True)
        if validator.validate(self.file_name_edit.text(), 0) == QtGui.QValidator.Intermediate:
            self.save_button.setEnabled(False)
            validator.blockSignals(block)
            return
        else:
            self.save_button.setEnabled(True)
        validator.blockSignals(block)

    def fileName(self):
        return self.file_name_edit.text().strip()

    def filePath(self):
        return self.file_path_edit.text().strip()


class CDFSaveDialog(FilenameAndPathDialog):
    def __init__(self, parent=None):
        super(CDFSaveDialog, self).__init__(parent=None)

        # create variable list
        var_label = label('Select Variables to Export')
        self.var_list = SelectionChangedListWidget()
        self.var_list.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.var_list.changedSelection.connect(self.update)
        var_layout = QtGui.QVBoxLayout()
        var_layout.addWidget(var_label)
        var_layout.addWidget(self.var_list)
        var_widget = QtGui.QWidget()
        var_widget.setLayout(var_layout)

        for var_label, var in get_variables().values:
            self.var_list.addItem(var_label)

        self.vertical_layout.insertWidget(0, self.var_list)

        self.setMinimumSize(500, 300)

        self.update()

    def update(self):
        if len(self.var_list.selectedIndexes()) == 0:
            self.save_button.setEnabled(False)
            return
        else:
            self.save_button.setEnabled(True)

        validator = self.file_path_edit.validator()
        block = validator.blockSignals(True)
        if validator.validate(self.file_path_edit.text(), 0) == QtGui.QValidator.Intermediate:
            self.save_button.setEnabled(False)
            validator.blockSignals(block)
            return
        else:
            self.save_button.setEnabled(True)
        validator.blockSignals(block)

        validator = self.file_name_edit.validator()
        block = validator.blockSignals(True)
        if validator.validate(self.file_name_edit.text(), 0) == QtGui.QValidator.Intermediate:
            self.save_button.setEnabled(False)
            validator.blockSignals(block)
            return
        else:
            self.save_button.setEnabled(True)
        validator.blockSignals(block)

    def getVariables(self):
        vars = []
        for index in self.var_list.selectedIndexes():
            vars.append(get_variables().get_variable(index.data()))
        return vars

    def accept(self):
        self.accepted.emit()


class ImageSaveDialog(FilenameAndPathDialog):
    def __init__(self, parent=None):
        super(ImageSaveDialog, self).__init__(parent=parent)


class MainMenu(QtGui.QMenuBar):
    def __init__(self, spreadsheet, var, gm, tmpl, parent=None):
        super(MainMenu, self).__init__(parent=parent)

        self.ss = spreadsheet
        self.var = var
        self.gm = gm
        self.tmpl = tmpl
        self.manipulations = Manipulations()
        self.dialog = None

        file_menu = self.addMenu("File")
        openscript = file_menu.addAction("Open Script")
        openscript.setShortcut(QtGui.QKeySequence.Open)
        openscript.triggered.connect(self.open_script)

        save = file_menu.addAction("Save Script")
        save.setShortcut(QtGui.QKeySequence.Save)
        save.triggered.connect(self.save_script)

        export_menu = file_menu.addMenu('Export')

        save_variables = export_menu.addAction('NetCDF File')
        save_variables.triggered.connect(self.launchCDFDailog)

        save_image = export_menu.addMenu('Image')
        save_image.triggered.connect(self.launchImageDialog)

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

    def launchCDFDailog(self):
        self.dialog = CDFSaveDialog()
        self.dialog.accepted.connect(self.saveCDF)
        self.dialog.show()
        self.dialog.raise_()

    def launchImageDialog(self):
        self.dialog = ImageSaveDialog()
        self.dialog.accepted.connect(self.saveImage)
        self.dialog.show()
        self.dialog.raise_()

    def saveCDF(self):
        global file_extensions
        filename = self.dialog.fileName()
        filepath = self.dialog.filePath()
        ext = filename.rfind('.')
        if ext == -1 or filename[ext + 1:] not in file_extensions:
            filename += '.nc'
        filepath = filepath.replace('\\', '/')

        if filepath[-1] != '/':
            filepath += '/'

        if not os.access(filepath, os.W_OK | os.X_OK):
            QtGui.QMessageBox.information(self, 'Invalid Permissions',
                                          "You do not have permission to acces the directory '{0}'".format(
                                              filepath))
            return

        if os.path.isfile(filepath + filename):
            buttons = QtGui.QMessageBox.warning(self, 'File Exists',
                                                'File {0} already exists at path {1}. Do you want to overwrite?'.format(
                                                    filename,
                                                    filepath),
                                                buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
            if buttons == QtGui.QMessageBox.Yes:
                os.remove(filepath + filename)
            else:
                return

        f = cdms2.createDataset(filepath + filename)
        for var in self.dialog.getVariables():
            f.write(var)

        f.close()

        self.dialog.close()
        self.dialog.deleteLater()

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
