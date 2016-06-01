import re
from PySide import QtGui, QtCore
from functools import partial

from cdatgui.bases.input_dialog import AccessibleButtonDialog
from bases.background_delegate import SaveItemDelegate
from cdatgui.cdat.importer import import_script
from cdatgui.cdat.exporter import export_script
from cdatgui.utils import label
from cdatgui.variables import get_variables
from cdatgui.variables.manager import manager
import os, cdms2, tempfile, shutil, vcs
from cdatgui.variables.manipulations.manipulation import Manipulations, SelectionChangedListWidget


class FileNameValidator(QtGui.QValidator):
    validInput = QtCore.Signal()
    invalidInput = QtCore.Signal()

    def __init__(self, parent=None):
        super(FileNameValidator, self).__init__(parent=parent)
        self.ext = '.nc'

    def validate(self, inp, pos):
        period_ind = inp.rfind('.')
        if self.isValidName(inp) and (period_ind != len(inp) - 1 and (period_ind == -1 or (
                        period_ind != -1 and inp[period_ind:] == self.ext))):
            self.validInput.emit()
            return QtGui.QValidator.Acceptable
        else:

            self.invalidInput.emit()
            return QtGui.QValidator.Intermediate

    def isValidName(self, name):
        return not (
            not re.search("^[a-zA-Z_]", name) or name == '' or re.search(' +', name) or re.search("[^a-zA-Z0-9_.]+",
                                                                                                  name))

    def setExt(self, comboItem):
        if comboItem == 'PNG':
            self.ext = '.png'
        elif comboItem == 'PDF':
            self.ext = '.pdf'
        elif comboItem == 'SVG':
            self.ext = '.svg'
        elif comboItem == 'Postscript':
            self.ext = '.ps'
        else:
            raise Exception('{0} is not a valid file extension'.format(comboItem))


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
        block = self.file_path_edit.validator().blockSignals(True)
        self.file_path_edit.setText('/')
        self.file_path_edit.validator().blockSignals(block)
        file_browser_button = QtGui.QPushButton('Browse')
        file_browser_button.clicked.connect(self.launchFileBrowser)
        file_path_layout = QtGui.QHBoxLayout()
        file_path_layout.addWidget(self.file_path_edit)
        file_path_layout.addWidget(file_browser_button)

        label_layout = QtGui.QVBoxLayout()
        label_layout.addWidget(label('Filename:'))
        label_layout.addWidget(label('Path:'))

        line_edit_layout = QtGui.QVBoxLayout()
        line_edit_layout.addWidget(self.file_name_edit)
        line_edit_layout.addLayout(file_path_layout)

        edits_layout = QtGui.QHBoxLayout()
        edits_layout.addLayout(label_layout)
        edits_layout.addLayout(line_edit_layout)

        self.vertical_layout.insertLayout(0, edits_layout)

        self.setMinimumSize(300, 200)

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

    def checkVarList(self):
        if len(self.var_list.selectedIndexes()) == 0:
            self.save_button.setEnabled(False)
            return
        else:
            self.save_button.setEnabled(True)

    def update(self):
        self.checkVarList()
        super(CDFSaveDialog, self).update()

    def getVariables(self):
        vars = []
        for index in self.var_list.selectedIndexes():
            vars.append(get_variables().get_variable(index.data()))
        return vars

    def getExtension(self):
        return '.nc'

    def accept(self):
        self.accepted.emit()


class TableLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super(TableLabel, self).__init__(parent=parent)
        self.selected = False
        self.pix = None

    def setSelected(self, selected):
        self.selected = selected
        if self.selected:
            pix = self.pixmap()
            painter = QtGui.QPainter(pix)
            # painter.save()
            color = QtGui.QColor(29, 28, 247)
            pen = QtGui.QPen(color, 10, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap, QtCore.Qt.MiterJoin)
            w = pen.width() / 2
            painter.setPen(pen)
            painter.drawRect(self.frameRect().adjusted(w, w, -w, -w))
            # painter.restore()
            self.setPixmap(pix)
        else:
            self.setPixmap(self.pix)

    def setPixmap(self, pixmap):
        if self.pix is None:
            self.pix = pixmap
        super(TableLabel, self).setPixmap(pixmap)


class ImageSaveDialog(FilenameAndPathDialog):
    def __init__(self, spreadsheet, parent=None):
        super(ImageSaveDialog, self).__init__(parent=parent)

        self.image_widget = QtGui.QTableWidget()
        self.image_widget.setItemDelegate(SaveItemDelegate())
        self.image_widget.itemSelectionChanged.connect(self.update)
        cells = spreadsheet.tabController.currentWidget().getCellWidgets()
        row_count, column_count = spreadsheet.tabController.currentWidget().getDimension()
        self.image_widget.setRowCount(row_count)
        self.image_widget.setColumnCount(column_count)
        row_size = 315
        column_size = 215
        width = row_size * column_count
        height = column_size * row_count
        self.image_widget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.image_widget.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.image_widget.setMaximumSize(width, height)

        selected_cells = spreadsheet.tabController.currentWidget().getSelectedCells()
        self.temp_dir = tempfile.mkdtemp()
        self.canvases = {}
        row = 0
        col = 0
        for ind, cell in enumerate(cells):
            path = os.path.join(self.temp_dir, 'grid_image_' + str(ind))
            image = cell.widget().canvas.png(path, width=100, height=100, units='pixel')
            loaded_image = QtGui.QImage(path)
            loaded_image = loaded_image.scaled(300, 200, transformMode=QtCore.Qt.SmoothTransformation)
            pixmap = QtGui.QPixmap.fromImage(loaded_image)

            lab = TableLabel()
            lab.setPixmap(pixmap)
            self.image_widget.setCellWidget(row, col, lab)
            self.canvases[(row, col)] = cell.widget().canvas

            # select if selected in spreadsheet
            if cell in selected_cells:
                sel = QtGui.QTableWidgetSelectionRange(row, col, row, col)
                self.image_widget.setRangeSelected(sel, True)

            if col < column_count - 1:
                col += 1
            else:
                row += 1
                col = 0

        seperator_frame = QtGui.QFrame()
        seperator_frame.setFrameShape(QtGui.QFrame.HLine)
        image_layout = QtGui.QHBoxLayout()
        image_layout.addWidget(self.image_widget)
        select_label = label('Select Canvases to Export:')
        select_label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        self.width = QtGui.QSpinBox()
        self.width.setMaximum(10000)
        self.width.setMinimum(1)
        self.height = QtGui.QSpinBox()
        self.height.setMaximum(10000)
        self.height.setMinimum(1)
        self.units = QtGui.QComboBox()
        self.units.addItems(['inches', 'in', 'cm', 'mm', 'pixels', 'dots'])

        self.file_type = QtGui.QComboBox()
        self.file_type.addItems(['PNG', 'PDF', 'SVG', 'Postscript'])
        self.file_type.currentIndexChanged[str].connect(self.setValidatorExt)
        self.file_name_edit.validator().setExt(self.file_type.currentText())

        attribute_row = QtGui.QHBoxLayout()
        attribute_row.addWidget(label('Width:'))
        attribute_row.addWidget(self.width)
        attribute_row.addWidget(label('Height:'))
        attribute_row.addWidget(self.height)
        attribute_row.addWidget(label('Units:'))
        attribute_row.addWidget(self.units)
        attribute_row.addWidget(label('Export As:'))
        attribute_row.addWidget(self.file_type)

        self.vertical_layout.insertWidget(0, select_label)
        self.vertical_layout.insertLayout(1, image_layout)
        self.vertical_layout.insertWidget(2, seperator_frame)
        self.vertical_layout.insertLayout(3, attribute_row)

        self.setMinimumSize(600, 700)

    def update(self):
        widgets = []
        for index in self.image_widget.selectedIndexes():
            widget = self.image_widget.cellWidget(index.row(), index.column())
            if widget is None:
                continue
            widget.setSelected(True)
            widgets.append(widget)

        for row in range(self.image_widget.rowCount()):
            for col in range(self.image_widget.columnCount()):
                widget = self.image_widget.cellWidget(row, col)
                if widget is None:
                    continue
                if widget not in widgets:
                    widget.setSelected(False)

        if not self.image_widget.selectedIndexes():
            self.save_button.setEnabled(False)
            return
        else:
            self.save_button.setEnabled(True)
        super(ImageSaveDialog, self).update()

    def setValidatorExt(self, comboItem):
        self.file_name_edit.validator().setExt(comboItem)
        self.file_name_edit.validator().validate(self.file_name_edit.text(), 0)

    def getExtension(self):
        item = self.file_type.currentText()
        if item == 'PNG':
            return '.png'
        elif item == 'PDF':
            return '.pdf'
        elif item == 'SVG':
            return '.svg'
        elif item == 'Postscript':
            return '.ps'
        else:
            raise Exception('{0} is not a valid file extension'.format(item))

    def removeImages(self):
        shutil.rmtree(self.temp_dir)

    def accept(self):
        self.accepted.emit()

    def close(self):
        super(ImageSaveDialog, self).close()
        self.removeImages()


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

        save_image = export_menu.addAction('Image')
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
        self.dialog.accepted.connect(partial(self.checkFile, self.saveCDF))
        self.dialog.show()
        self.dialog.raise_()

    def launchImageDialog(self):
        self.dialog = ImageSaveDialog(self.ss)
        self.dialog.accepted.connect(partial(self.checkFile, self.saveImage))
        self.dialog.show()
        self.dialog.raise_()

    def saveImage(self, filepath, filename, ext):
        indicies = self.dialog.image_widget.selectedIndexes()

        w, h = self.dialog.canvases[(indicies[0].row(), indicies[0].column())]._compute_width_height(
            self.dialog.width.value(), self.dialog.height.value(), self.dialog.units.currentText())

        render_canvas = vcs.init(geometry=(w, h), bg=True)
        render_canvas.open()
        for count, index in enumerate(indicies):
            canvas = self.dialog.canvases[(index.row(), index.column())]
            render_canvas.display_names = canvas.display_names
            render_canvas.update()

            if self.dialog.file_type.currentText() == 'PNG':
                func = render_canvas.png
            elif self.dialog.file_type.currentText() == 'PDF':
                func = render_canvas.pdf
            elif self.dialog.file_type.currentText() == 'SVG':
                func = render_canvas.svg
            elif self.dialog.file_type.currentText() == 'Postscript':
                func = render_canvas.postscript

            if count:
                filename = '{0}_{1}'.format(filename, count)

            file = '{0}{1}.{2}'.format(filepath, filename, ext)
            if not self.checkIfFileExists(file):
                return

            func(file)

            if count:
                filename = filename.split('.')[0][:-2]

        self.dialog.close()
        self.dialog.deleteLater()
        self.dialog = None

    def checkIfFileExists(self, file):
        print "checking if file exists", file
        if os.path.isfile(file):
            buttons = QtGui.QMessageBox.warning(self, 'File Exists',
                                                'File {0} already exists. Do you want to overwrite?'.format(file),
                                                buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
            if buttons == QtGui.QMessageBox.Yes:
                os.remove(file)
            else:
                return False
        return True

    def checkFile(self, func):
        filename = self.dialog.fileName()
        filepath = self.dialog.filePath()
        extension = self.dialog.getExtension()
        ext = filename.rfind('.')

        filepath = filepath.replace('\\', '/')

        if filepath[-1] != '/':
            filepath += '/'

        if not os.access(filepath, os.W_OK | os.X_OK):
            QtGui.QMessageBox.information(self, 'Invalid Permissions',
                                          "You do not have permission to access the directory '{0}'".format(
                                              filepath))
            return

        if ext == -1 or filename[ext:] != extension:
            filename += extension

        filename, ext = filename.split('.')

        func(filepath, filename, ext)

    def saveCDF(self, filepath, filename):
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
