from functools import partial

from PySide import QtCore, QtGui
from cdatgui.bases.input_dialog import ValidatingInputDialog, AccessibleButtonDialog
from cdatgui.utils import label
from cdatgui.variables import get_variables
from cdatgui.variables.variable_add import FileNameValidator
import cdutil, cdtime, genutil, cdms2


def getTimes(var):
    time = var.getTime()

    months = set()
    times = []
    for t in time:
        reltime = cdtime.reltime(t, time.units)
        comptime = reltime.tocomponent()
        months.add(comptime.month)
    if 12 in months and 1 in months and 2 in months:
        times.append('DJF')
    if 3 in months and 4 in months and 5 in months:
        times.append('MAM')
    if 6 in months and 7 in months and 8 in months:
        times.append('JJA')
    if 9 in months and 10 in months and 11 in months:
        times.append('SON')

    for i in range(1, 13):
        if i not in months:
            break
    else:
        times.append('YEAR')
        times.append('ANNUALCYCLE')

    for ind, item in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT',
                                'NOV', 'DEC']):
        if ind + 1 in months:
            times.append(item)
    return times


class VariableSelectorDialog(AccessibleButtonDialog):
    def __init__(self, parent=None):
        super(VariableSelectorDialog, self).__init__(parent=parent)
        self.variable_combo = QtGui.QComboBox()
        self.variable_combo.setModel(get_variables())

        variable_label = label("Variable:")

        variable_layout = QtGui.QHBoxLayout()
        variable_layout.addWidget(variable_label)
        variable_layout.addWidget(self.variable_combo)

        self.vertical_layout.insertLayout(0, variable_layout)

        self.save_button.setText('Save as')

    def getVarName(self):
        return self.variable_combo.currentText()

    def getVar(self):
        return get_variables().get_variable(self.variable_combo.currentText())

    def accept(self):
        self.accepted.emit()


class LinearRegressionDialog(VariableSelectorDialog):
    def __init__(self, parent=None):
        super(LinearRegressionDialog, self).__init__(parent=parent)
        self.regressionType = None
        self.variable_combo.currentIndexChanged.connect(self.populateLists)

        self.tab_widget = QtGui.QTabWidget()
        self.tab_widget.currentChanged.connect(self.updateRegressionType)

        self.second_var_combo = QtGui.QComboBox()
        second_label = label('Regression over:')
        second_layout = QtGui.QHBoxLayout()
        second_layout.addWidget(second_label)
        second_layout.addWidget(self.second_var_combo)
        second_var_widget = QtGui.QWidget()
        second_var_widget.setLayout(second_layout)
        self.tab_widget.addTab(second_var_widget, 'Variable')

        self.axis_combo = QtGui.QComboBox()
        axis_label = label('Axis:')
        axis_layout = QtGui.QHBoxLayout()
        axis_layout.addWidget(axis_label)
        axis_layout.addWidget(self.axis_combo)
        axis_widget = QtGui.QWidget()
        axis_widget.setLayout(axis_layout)
        self.tab_widget.addTab(axis_widget, 'Axis')

        self.populateAxisCombo()
        self.populateSecondVarCombo()
        self.updateRegressionType()
        self.vertical_layout.insertWidget(1, self.tab_widget)

    def getSecondItemName(self):
        if self.regressionType == 'axis':
            return self.axis_combo.currentText()
        elif self.regressionType == 'variable':
            return self.second_var_combo.currentText()
        else:
            return None

    def updateRegressionType(self):
        self.regressionType = self.tab_widget.tabText(self.tab_widget.currentIndex()).lower()

        if self.regressionType == 'axis':
            if self.axis_combo.count() == 0:
                self.save_button.setEnabled(False)
            else:
                self.save_button.setEnabled(True)
        elif self.regressionType == 'variable':
            if self.second_var_combo.count() == 0:
                self.save_button.setEnabled(False)
            else:
                self.save_button.setEnabled(True)
        elif self.regressionType == 'none':
            self.save_button.setEnabled(True)

    def populateLists(self):
        self.populateAxisCombo()
        self.populateSecondVarCombo()

        if self.regressionType == 'variable':
            if self.second_var_combo.count() == 0:
                self.save_button.setEnabled(False)
            else:
                self.save_button.setEnabled(True)
        elif self.regressionType == 'axis':
            if self.axis_combo.count() == 0:
                self.save_button.setEnabled(False)
            else:
                self.save_button.setEnabled(True)
        elif self.regressionType == 'none':
            self.save_button.setEnabled(True)

    def populateSecondVarCombo(self):
        for row in range(self.second_var_combo.count()):
            self.second_var_combo.removeItem(0)

        for var_label, list_var in get_variables().values:
            if var_label != self.getVarName() and list_var.shape == self.getVar().shape:
                self.second_var_combo.addItem(var_label)

    def populateAxisCombo(self):
        for _ in range(self.axis_combo.count()):
            self.axis_combo.removeItem(0)

        for axis in self.getVar().getAxisList():
            self.axis_combo.addItem(axis.id)

    def getAxis(self):
        if self.regressionType == 'axis':
            return str(self.axis_combo.currentText())
        else:
            return None

    def getSecondVar(self):
        if self.regressionType == 'variable':
            return get_variables().get_variable(self.second_var_combo.currentText())
        else:
            return None

    def getSecondVarName(self):
        return self.second_var_combo.currentText()


class DoubleVarDialog(VariableSelectorDialog):
    def __init__(self, parent=None):
        super(DoubleVarDialog, self).__init__(parent=parent)

        self.second_label = label('Correlate with:')
        self.second_var_combo = QtGui.QComboBox()

        self.variable_combo.currentIndexChanged.connect(self.populateSecondVarList)

        self.populateSecondVarList()

        second_var_layout = QtGui.QHBoxLayout()
        second_var_layout.addWidget(self.second_label)
        second_var_layout.addWidget(self.second_var_combo)

        self.vertical_layout.insertLayout(1, second_var_layout)

    def setSecondLabel(self, text):
        self.second_label.setText(text)

    def populateSecondVarList(self):
        for _ in range(self.second_var_combo.count()):
            self.second_var_combo.removeItem(0)

        for var_label, list_var in get_variables().values:
            if var_label != self.getVarName() and list_var.shape == self.getVar().shape:
                self.second_var_combo.addItem(var_label)

        if self.second_var_combo.count() == 0:
            self.save_button.setEnabled(False)
        else:
            self.save_button.setEnabled(True)

    def getSecondVar(self):
        return get_variables().get_variable(self.second_var_combo.currentText())

    def getSecondVarName(self):
        return self.second_var_combo.currentText()


class AxisSelectorDialog(VariableSelectorDialog):
    def __init__(self, parent=None):
        super(AxisSelectorDialog, self).__init__(parent=parent)

        self.variable_combo.currentIndexChanged.connect(self.changeAxis)

        axis_label = label('Axis:')

        self.axis_combo = QtGui.QComboBox()

        axis_layout = QtGui.QHBoxLayout()
        axis_layout.addWidget(axis_label)
        axis_layout.addWidget(self.axis_combo)
        self.vertical_layout.insertLayout(1, axis_layout)

        self.populateAxisCombo()

    def changeAxis(self, index):
        for _ in range(self.axis_combo.count()):
            self.axis_combo.removeItem(0)
        self.populateAxisCombo()

    def populateAxisCombo(self):
        for axis in self.getVar().getAxisList():
            self.axis_combo.addItem(axis.id)

    def getAxis(self):
        return str(self.axis_combo.currentText())


class DepartureDialog(VariableSelectorDialog):
    def __init__(self, parent=None):
        super(DepartureDialog, self).__init__(parent=parent)

        self.variable_combo.currentIndexChanged.connect(self.populateDepartures)

        self.departure_combo = QtGui.QComboBox()
        self.populateDepartures()
        self.departure_combo.currentIndexChanged.connect(self.toggleBounds)

        departure_label = label("Departure:")

        departure_layout = QtGui.QHBoxLayout()
        departure_layout.addWidget(departure_label)
        departure_layout.addWidget(self.departure_combo)

        self.vertical_layout.insertLayout(1, departure_layout)

        self.bounds_combo = QtGui.QComboBox()
        self.bounds_combo.addItems(['Daily', 'Monthly', 'Yearly'])

        bounds_label = label('Bounds:')

        bounds_layout = QtGui.QHBoxLayout()
        bounds_layout.addWidget(bounds_label)
        bounds_layout.addWidget(self.bounds_combo)

        self.vertical_layout.insertLayout(2, bounds_layout)

    def toggleBounds(self, index):
        if self.departure_combo.currentText() in ['DJF', 'MAM', 'JJA', 'SON', 'YEAR']:
            self.bounds_combo.setEnabled(True)
        else:
            self.bounds_combo.setEnabled(False)

    def getDeparture(self):
        return self.departure_combo.currentText()

    def getBounds(self):
        return self.bounds_combo.currentText()

    def populateDepartures(self):
        times = getTimes(self.getVar())
        for _ in range(self.departure_combo.count()):
            self.departure_combo.removeItem(0)
        for item in times:
            self.departure_combo.addItem(item)


class ClimatologyDialog(VariableSelectorDialog):
    def __init__(self, climo_type, parent=None):
        super(ClimatologyDialog, self).__init__(parent=parent)

        self.variable_combo.currentIndexChanged.connect(self.populateClimos)
        self.climo_type = climo_type
        self.climo_combo = QtGui.QComboBox()
        self.populateClimos()
        clim_label = label("Climatology:")

        clim_layout = QtGui.QHBoxLayout()
        clim_layout.addWidget(clim_label)
        clim_layout.addWidget(self.climo_combo)

        self.vertical_layout.insertLayout(1, clim_layout)

        if climo_type == 'seasonal':
            self.bounds_combo = QtGui.QComboBox()
            self.bounds_combo.addItems(['Daily', 'Monthly', 'Yearly'])

            bounds_label = label('Bounds:')

            bounds_layout = QtGui.QHBoxLayout()
            bounds_layout.addWidget(bounds_label)
            bounds_layout.addWidget(self.bounds_combo)

            self.vertical_layout.insertLayout(2, bounds_layout)

    def getClimatology(self):
        return self.climo_combo.currentText()

    def getBounds(self):
        return self.bounds_combo.currentText()

    def populateClimos(self):
        seasons = ['DJF', 'MAM', 'JJA', 'SON', 'YEAR']
        times = getTimes(self.getVar())
        for _ in range(self.climo_combo.count()):
            self.climo_combo.removeItem(0)
        for item in times:
            if self.climo_type == 'seasonal' and item in seasons:
                self.climo_combo.addItem(item)
            elif self.climo_type == 'monthly' and item not in seasons:
                self.climo_combo.addItem(item)


class RegridDialog(VariableSelectorDialog):
    def __init__(self, parent=None):
        super(RegridDialog, self).__init__(parent=parent)

        self.source_grid_combo = QtGui.QComboBox()
        for v_label, var in get_variables().values:
            if var.getGrid() is not None:
                self.source_grid_combo.addItem(
                    '{0} {1}'.format(v_label, var.getGrid().shape))

        source_grid_label = label("Source Grid:")

        source_grid_layout = QtGui.QHBoxLayout()
        source_grid_layout.addWidget(source_grid_label)
        source_grid_layout.addWidget(self.source_grid_combo)

        self.regrid_tool_combo = QtGui.QComboBox()
        self.regrid_tool_combo.addItems(['regrid2', 'esmf', 'libcf'])
        self.regrid_tool_combo.currentIndexChanged.connect(self.updateRegridMethod)

        regrid_tool_label = label("Regrid Tool:")

        regrid_tool_layout = QtGui.QHBoxLayout()
        regrid_tool_layout.addWidget(regrid_tool_label)
        regrid_tool_layout.addWidget(self.regrid_tool_combo)

        self.regrid_method_combo = QtGui.QComboBox()
        self.regrid_method_combo.addItems(['conserve', 'linear', 'patch'])
        self.regrid_method_combo.setEnabled(False)

        regrid_method_label = label("Regrid Method:")

        regrid_method_layout = QtGui.QHBoxLayout()
        regrid_method_layout.addWidget(regrid_method_label)
        regrid_method_layout.addWidget(self.regrid_method_combo)

        self.vertical_layout.insertLayout(1, source_grid_layout)
        self.vertical_layout.insertLayout(2, regrid_tool_layout)
        self.vertical_layout.insertLayout(3, regrid_method_layout)

    def updateRegridMethod(self, index):
        if self.regrid_tool_combo.currentText() == 'esmf':
            self.regrid_method_combo.setEnabled(True)
        else:
            self.regrid_method_combo.setEnabled(False)

    def getSourceVarName(self):
        return self.source_grid_combo.currentText().split(" ")[0]

    def getRegridTool(self):
        return self.regrid_tool_combo.currentText()

    def getRegridMethod(self):
        if self.regrid_method_combo.isEnabled():
            return self.regrid_method_combo.currentText()
        return None


class AxisListWidget(QtGui.QListWidget):
    changedSelection = QtCore.Signal()

    def selectionChanged(self, selected, deselected):
        super(AxisListWidget, self).selectionChanged(selected, deselected)
        self.changedSelection.emit()


class AverageDialog(VariableSelectorDialog):
    def __init__(self, parent=None):
        super(AverageDialog, self).__init__(parent=parent)
        self.variable_combo.currentIndexChanged.connect(self.update)

        self.axis_list = AxisListWidget()
        self.axis_list.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.axis_list.changedSelection.connect(self.selectionChanged)

        axis_label = label('Axis:')

        axis_layout = QtGui.QHBoxLayout()
        axis_layout.addWidget(axis_label)
        axis_layout.addWidget(self.axis_list)

        self.bounds_combo = QtGui.QComboBox()
        self.bounds_combo.addItems(['Auto', 'Daily', 'Monthly', 'Yearly'])
        self.bounds_combo.setEnabled(False)

        bounds_label = label('Time bounds:')

        bounds_layout = QtGui.QHBoxLayout()
        bounds_layout.addWidget(bounds_label)
        bounds_layout.addWidget(self.bounds_combo)

        self.vertical_layout.insertLayout(1, axis_layout)
        self.vertical_layout.insertLayout(2, bounds_layout)

        self.update()
        self.save_button.setEnabled(False)

    def update(self):
        var = self.getVar()
        time_axis = var.getTime()
        try:
            bounds = time_axis.getBounds()
            if bounds is not None:
                self.bounds_combo.insertItem(0, 'Original bounds')
        except AttributeError:
            pass

        for _ in range(self.axis_list.count()):
            widgetitem = self.axis_list.takeItem(0)
            del widgetitem
        self.populateAxisList()

    def populateAxisList(self):
        for axis in self.getVar().getAxisList():
            self.axis_list.addItem(axis.id)

    def selectionChanged(self):
        if len(self.axis_list.selectedIndexes()) > 0:
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)

        try:
            for ind in self.axis_list.selectedIndexes():
                if ind.data().lower() == self.getVar().getTime().id:
                    self.bounds_combo.setEnabled(True)
                    return
        except AttributeError:
            pass

        self.bounds_combo.setEnabled(False)

    def getAxis(self):
        selected_axis = []
        for ind in self.axis_list.selectedIndexes():
            selected_axis.append(str(self.getVar().getAxisIndex(str(ind.data()))))
        return ''.join(selected_axis)

    def getAxisCharacters(self):
        selected_axis = []
        for ind in self.axis_list.selectedIndexes():
            selected_axis.append(str(ind.data()[0].lower()))
        return ''.join(selected_axis)

    def getBounds(self):
        return self.bounds_combo.currentText()


class DoubleNameDialog(ValidatingInputDialog):
    def __init__(self, parent=None):
        super(DoubleNameDialog, self).__init__(parent=parent)

        self.setLabelText('Slope Name:')

        self.second_name_edit = QtGui.QLineEdit()
        second_name_label = label('Intercept Name:')
        second_name_layout = QtGui.QHBoxLayout()
        second_name_layout.addWidget(second_name_label)
        second_name_layout.addWidget(self.second_name_edit)
        self.vertical_layout.insertLayout(1, second_name_layout)

    def secondTextValue(self):
        return self.second_name_edit.text().strip()

    def setSecondNameValidator(self, validator):
        self.second_name_edit.setValidator(validator)

        try:
            validator.invalidInput.connect(lambda: self.save_button.setEnabled(False))
            validator.validInput.connect(lambda: self.save_button.setEnabled(True))
        except AttributeError:
            pass

    def setSecondTextValue(self, text):
        self.second_name_edit.setText(text)


class Manipulations(QtCore.QObject):
    remove = QtCore.Signal(object)

    def __init__(self):
        super(Manipulations, self).__init__()
        self.dialog = None
        self.name_dialog = None

    def launchClimatologyDialog(self, ctype):
        self.dialog = ClimatologyDialog(ctype)
        self.dialog.accepted.connect(partial(self.getClimoSuggestedName, ctype))
        self.dialog.rejected.connect(self.dialog.deleteLater)
        self.dialog.setMinimumSize(300, 200)
        self.dialog.setWindowTitle('Climatology')
        self.dialog.show()
        self.dialog.raise_()

    def launchAverageDialog(self):
        self.dialog = AverageDialog()
        self.dialog.accepted.connect(self.getAverageSuggestedName)
        self.dialog.rejected.connect(self.dialog.deleteLater)
        self.dialog.setWindowTitle('Average')
        self.dialog.show()
        self.dialog.raise_()

    def launchRegridDialog(self):
        self.dialog = RegridDialog()
        self.dialog.accepted.connect(self.getRegridSuggestedName)
        self.dialog.rejected.connect(self.dialog.deleteLater)
        self.dialog.setWindowTitle('Regrid')
        self.dialog.show()
        self.dialog.raise_()

    def getAverageSuggestedName(self):
        text = '{0}_average_over_{1}'.format(self.dialog.getVarName(), self.dialog.getAxisCharacters())

        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.average)

    def getRegridSuggestedName(self):
        text = '{0}_regrid_from_{1}_{2}'.format(self.dialog.getVarName(), self.dialog.getSourceVarName(),
                                                self.dialog.getRegridTool())
        if self.dialog.getRegridMethod():
            text += '_' + str(self.dialog.getRegridMethod())

        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.regrid)

    def getClimoSuggestedName(self, ctype):
        if ctype == 'seasonal':
            text = '{0}_{1}_{2}_climatology'.format(self.dialog.getClimatology(), self.dialog.getBounds().lower(),
                                                    self.dialog.getVarName())
        else:
            text = '{0}_{1}_climatology'.format(self.dialog.getClimatology(), self.dialog.getVarName())

        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.climatology)

    def launchNameDialog(self, suggested_name, callback):
        self.name_dialog = ValidatingInputDialog()
        self.name_dialog.setValidator(FileNameValidator())
        self.name_dialog.setWindowTitle("Save As")
        self.name_dialog.setLabelText('Enter New Name:')

        self.name_dialog.setTextValue(suggested_name)
        self.name_dialog.edit.selectAll()
        self.name_dialog.accepted.connect(callback)
        self.name_dialog.rejected.connect(self.name_dialog.deleteLater)
        self.name_dialog.show()
        self.name_dialog.raise_()

    def regrid(self):
        var_name = self.dialog.getVarName()
        var = get_variables().get_variable(var_name)
        source_var_name = self.dialog.getSourceVarName()
        source_var = get_variables().get_variable(source_var_name)
        regrid_tool = self.dialog.getRegridTool()
        kargs = {'regrid_tool': regrid_tool}
        if regrid_tool == 'esmf':
            kargs['regrid_method'] = self.dialog.getRegridMethod()
        elif regrid_tool == 'libcf':
            kargs['regrid_method'] = 'linear'

        # spits out filemetadatawrapper :D
        new_var = var.regrid(source_var.getGrid(), **kargs)
        new_var.id = self.name_dialog.textValue()

        get_variables().add_variable(new_var)

        self.dialog.close()
        self.dialog.deleteLater()

        self.name_dialog.close()
        self.name_dialog.deleteLater()

    def average(self, var=None, axis_id=None):
        if var is None and axis_id is None:
            from_edit_var = False
            var_name = self.dialog.getVarName()
            var = get_variables().get_variable(var_name)

            axis = self.dialog.getAxis()
            # determine if time is part of selected indices
            time = False
            for ind in axis:
                ind = int(ind)
                if var.getAxis(ind) == var.getTime():
                    time = True

            if time:
                time_axis = var.getTime()
                bounds = self.dialog.getBounds()
                if bounds == 'Auto':
                    time_axis.setBounds(time_axis.genGenericBounds())
                elif bounds != 'Original bounds':
                    self.setBounds(time_axis, bounds)
        elif (var is None and axis_id is not None) or (var is not None and axis_id is None):
            raise Exception("You provided one of two variables needed for averaging. Aborting")
        else:
            from_edit_var = True
            axis_index = var.getAxisIndex(axis_id)
            axis = str(axis_index)
            time = False
            for ind in axis:
                ind = int(ind)
                if var.getAxis(ind) == var.getTime():
                    time = True
            if time:
                time_axis = var.getTime()
                time_axis.setBounds(time_axis.genGenericBounds())

        # set all axis to autolevels if isLevel
        for axis_obj in var.getAxisList():
            if axis_obj.isLevel():
                axis_obj.setBounds(axis_obj.genGenericBounds())

        # get axis list to re add axis to var after summation
        axis_list = var.getAxisList()
        for ind in axis:
            axis_list.pop(int(ind))

        new_var = cdutil.averager(var, axis=axis)

        for index, axis in enumerate(axis_list):
            new_var.setAxis(index, axis)

        if from_edit_var:
            new_var.id = str(var.id)
        else:
            new_var.id = str(self.name_dialog.textValue())
            get_variables().add_variable(new_var)

        if self.dialog:
            self.dialog.close()
            self.dialog.deleteLater()

        if self.name_dialog:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

        if from_edit_var:
            return new_var

    def climatology(self):
        climo = self.dialog.getClimatology()
        var_name = self.dialog.getVarName()
        var = get_variables().get_variable(var_name)
        var = var.var

        if climo in ['DJF', 'MAM', 'JJA', 'SON', 'YEAR']:
            bounds = self.dialog.getBounds()
            time_axis = var.getTime()
            self.setBounds(time_axis, bounds)
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
        elif climo == 'ANNUALCYCLE':
            new_var = cdutil.ANNUALCYCLE.climatology(var)
        else:
            raise Exception(climo + " is not a valid climatology")

        new_var.id = self.name_dialog.textValue()
        get_variables().add_variable(new_var)

        # cleanup
        self.dialog.close()
        self.dialog.deleteLater()

        self.name_dialog.close()
        self.name_dialog.deleteLater()

    def setBounds(self, time_axis, bounds):
        if bounds == "Daily":
            cdutil.setAxisTimeBoundsDaily(time_axis)
        elif bounds == "Monthly":
            cdutil.setAxisTimeBoundsMonthly(time_axis)
        elif bounds == "Yearly":
            cdutil.setAxisTimeBoundsYearly(time_axis)
        else:
            raise ValueError("No bounds function for %s" % bounds)

    def launchSumDialog(self):
        self.dialog = AxisSelectorDialog()
        self.dialog.accepted.connect(self.getSumSuggestedName)
        self.dialog.setWindowTitle('Summation')
        self.dialog.show()
        self.dialog.raise_()

    def launchSTDDialog(self):
        self.dialog = AxisSelectorDialog()
        self.dialog.accepted.connect(self.getSTDSuggestedName)
        self.dialog.setWindowTitle('Standard Deviation')
        self.dialog.show()
        self.dialog.raise_()

    def adjustNameForDuplicates(self, text):
        count = 1
        while get_variables().variable_exists(text):
            if count == 1:
                text = text + '_' + str(count)
            else:
                text = text[:-2] + '_' + str(count)
            count += 1
        return text

    def getSumSuggestedName(self):
        text = '{0}_sum_over_{1}'.format(self.dialog.getVarName(), self.dialog.getAxis())
        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.sum)

    def sum(self, var=None, axis_id=None):
        if var is None and axis_id is None:
            from_edit_var = False
            var = self.dialog.getVar()
            axis = self.dialog.getAxis()
            axis_index = var.getAxisIndex(axis)
            if axis_index == -1:
                raise Exception("Invalid axis cannot perform summation")
        elif (var is None and axis_id is not None) or (var is not None and axis_id is None):
            raise Exception("You provided one of two variables needed for summation. Aborting")
        else:
            from_edit_var = True
            axis_index = var.getAxisIds().index(axis_id)
            if axis_index == -1:
                raise Exception("Invalid axis cannot perform summation")
        # get axis list to re add axis to var after summation
        axis_list = var.getAxisList()
        axis_list.pop(axis_index)

        # create var
        new_var = var.sum(axis_index)

        # add old axis
        for index, axis in enumerate(axis_list):
            new_var.setAxis(index, axis)

        if from_edit_var:
            new_var.id = str(var.id)
        else:
            new_var.id = str(self.name_dialog.textValue())
            get_variables().add_variable(new_var)

        if self.dialog:
            self.dialog.close()
            self.dialog.deleteLater()
        if self.name_dialog is not None:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

        if from_edit_var:
            return new_var

    def getSTDSuggestedName(self):
        text = '{0}_std_over_{1}'.format(self.dialog.getVarName(), self.dialog.getAxis())
        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.std)

    def getDepartureSuggestedName(self):
        if self.dialog.bounds_combo.isEnabled():
            text = '{0}_{1}_departure_for_{2}'.format(self.dialog.getVarName(), self.dialog.getBounds(),
                                                      self.dialog.getDeparture())
        else:
            text = '{0}_departure_for_{1}'.format(self.dialog.getVarName(), self.dialog.getDeparture())
        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.departure)

    def std(self, var=None, axis_id=None):
        if var is None and axis_id is None:
            from_edit_var = False
            var = self.dialog.getVar()
            axis = self.dialog.getAxis()
            axis_index = var.getAxisIndex(axis)
            if axis_index == -1:
                raise Exception("Invalid axis cannot perform summation")
        elif (var is None and axis_id is not None) or (var is not None and axis_id is None):
            raise Exception("You provided one of two variables needed for summation. Aborting")
        else:
            from_edit_var = True
            axis_index = var.getAxisIds().index(axis_id)
            if axis_index == -1:
                raise Exception("Invalid axis cannot perform summation")
        # get axis list to re add axis to var after summation
        axis_list = var.getAxisList()
        axis_list.pop(axis_index)

        # create var
        new_var = var.std(axis_index)
        new_var = cdms2.MV2.asVariable(new_var)

        # add old axis
        for index, axis in enumerate(axis_list):
            new_var.setAxis(index, axis)

        if from_edit_var:
            new_var.id = str(var.id)
        else:
            new_var.id = str(self.name_dialog.textValue())
            get_variables().add_variable(new_var)

        if self.dialog:
            self.dialog.close()
            self.dialog.deleteLater()
        if self.name_dialog is not None:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

        if from_edit_var:
            return new_var

    def launchDepartureDialog(self):
        self.dialog = DepartureDialog()
        self.dialog.accepted.connect(self.getDepartureSuggestedName)
        self.dialog.setWindowTitle('Departure')
        self.dialog.show()
        self.dialog.raise_()

    def departure(self):
        departure = self.dialog.getDeparture()
        var_name = self.dialog.getVarName()
        var = get_variables().get_variable(var_name)
        var = var.var

        if departure in ['DJF', 'MAM', 'JJA', 'SON', 'YEAR']:
            bounds = self.dialog.getBounds()
            time_axis = var.getTime()
            self.setBounds(time_axis, bounds)
        else:
            time_axis = var.getTime()
            cdutil.setAxisTimeBoundsMonthly(time_axis)

        if departure == "DJF":
            new_var = cdutil.DJF.departures(var)
        elif departure == "MAM":
            new_var = cdutil.MAM.departures(var)
        elif departure == "JJA":
            new_var = cdutil.JJA.departures(var)
        elif departure == "SON":
            new_var = cdutil.SON.departures(var)
        elif departure == "YEAR":
            new_var = cdutil.YEAR.departures(var)
        elif departure == 'JAN':
            new_var = cdutil.JAN.departures(var)
        elif departure == 'FEB':
            new_var = cdutil.FEB.departures(var)
        elif departure == 'MAR':
            new_var = cdutil.MAR.departures(var)
        elif departure == 'APR':
            new_var = cdutil.APR.departures(var)
        elif departure == 'MAY':
            new_var = cdutil.MAY.departures(var)
        elif departure == 'JUN':
            new_var = cdutil.JUN.departures(var)
        elif departure == 'JUL':
            new_var = cdutil.JUL.departures(var)
        elif departure == 'AUG':
            new_var = cdutil.AUG.departures(var)
        elif departure == 'SEP':
            new_var = cdutil.SEP.departures(var)
        elif departure == 'OCT':
            new_var = cdutil.OCT.departures(var)
        elif departure == 'NOV':
            new_var = cdutil.NOV.departures(var)
        elif departure == 'DEC':
            new_var = cdutil.DEC.departures(var)
        elif departure == 'ANNUALCYCLE':
            new_var = cdutil.ANNUALCYCLE.departures(var)
        else:
            raise Exception('Did not provide a valid climatology')

        new_var.id = self.name_dialog.textValue()

        get_variables().add_variable(new_var)

        # cleanup
        self.dialog.close()
        self.dialog.deleteLater()

        if self.name_dialog is not None:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

    def launchCorrelationOrCovarianceDialog(self, operation):
        if operation == 'Correlation':
            func = genutil.statistics.correlation
        elif operation == 'Covariance':
            func = genutil.statistics.covariance
        elif operation == 'Lagged Correlation':
            func = genutil.statistics.laggedcorrelation
        elif operation == 'Lagged Covariance':
            func = genutil.statistics.laggedcovariance
        else:
            raise NotImplementedError('No function for operation ' + operation)
        operation = operation.replace(' ', '_')

        self.dialog = DoubleVarDialog()
        self.dialog.setWindowTitle(operation)
        self.dialog.accepted.connect(partial(self.getCorrelationOrCovarianceSuggestedName, func, operation.lower()))

        self.dialog.setSecondLabel(operation + ' with:')
        self.dialog.show()
        self.dialog.raise_()

    def getCorrelationOrCovarianceSuggestedName(self, func, operation):
        text = '{0}_{1}_with_{2}'.format(self.dialog.getVarName(), operation, self.dialog.getSecondVarName())
        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, partial(self.correlationOrCovariance, func))

    def correlationOrCovariance(self, func):
        var1 = self.dialog.getVar()
        var2 = self.dialog.getSecondVar()

        new_var = func(var1, var2)

        new_var.id = self.name_dialog.textValue()

        get_variables().add_variable(new_var)

        self.dialog.close()
        self.dialog.deleteLater()

        if self.name_dialog:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

    def launchLinearRegressionDialog(self):
        self.dialog = LinearRegressionDialog()
        self.dialog.accepted.connect(self.getLinearRegressionSuggestedName)
        self.dialog.setWindowTitle('Linear Regression')
        self.dialog.show()
        self.dialog.raise_()

    def getLinearRegressionSuggestedName(self):
        if self.dialog.getSecondItemName() is not None:
            slope_text = '{0}_over_{1}_slope'.format(self.dialog.getVarName(), self.dialog.getSecondItemName())
            intercept_text = '{0}_over_{1}_intercept'.format(self.dialog.getVarName(), self.dialog.getSecondItemName())
        else:
            slope_text = '{0}_linear_regression_slope'.format(self.dialog.getVarName())
            intercept_text = '{0}_linear_regression_intercept'.format(self.dialog.getVarName())

        slope_text = self.adjustNameForDuplicates(slope_text)
        intercept_text = self.adjustNameForDuplicates(intercept_text)

        self.launchDoubleNameDialog(slope_text, intercept_text, self.linearRegression)

    def launchDoubleNameDialog(self, slope_suggested_name, intercept_suggested_name, callback):
        self.name_dialog = DoubleNameDialog()
        self.name_dialog.setValidator(FileNameValidator())
        self.name_dialog.setSecondNameValidator(FileNameValidator())
        self.name_dialog.setWindowTitle("Save As")

        self.name_dialog.setTextValue(slope_suggested_name)
        self.name_dialog.setSecondTextValue(intercept_suggested_name)
        self.name_dialog.edit.selectAll()
        self.name_dialog.accepted.connect(callback)
        self.name_dialog.rejected.connect(self.name_dialog.deleteLater)
        self.name_dialog.show()
        self.name_dialog.raise_()

    def linearRegression(self):
        var = self.dialog.getVar()
        if self.dialog.regressionType == 'axis':
            axis = self.dialog.getAxis()
            axis_ind = var.getAxisIndex(axis)
            slope, intercept = genutil.statistics.linearregression(var, axis=axis_ind)
        elif self.dialog.regressionType == 'variable':
            var2 = self.dialog.getSecondVar()
            slope, intercept = genutil.statistics.linearregression(var, x=var2)
        elif self.dialog.regressionType == 'none':
            slope, intercept = genutil.statistics.linearregression(var)
        else:
            raise Exception("Uh oh! Invalid regression type " + self.dialog.regressionType)

        slope.id = self.name_dialog.textValue()
        intercept.id = self.name_dialog.secondTextValue()

        get_variables().add_variable(slope)
        get_variables().add_variable(intercept)

        self.dialog.close()
        self.dialog.deleteLater()

        if self.name_dialog:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

    def geometricMean(self, var=None, axis_id=None):
        if var is None and axis_id is None:
            from_edit_var = False
            var = self.dialog.getVar()
            axis = self.dialog.getAxis()
            axis_index = var.getAxisIndex(axis)
            if axis_index == -1:
                raise Exception("Invalid axis cannot perform summation")
        elif (var is None and axis_id is not None) or (var is not None and axis_id is None):
            raise Exception("You provided one of two variables needed for summation. Aborting")
        else:
            from_edit_var = True
            axis_index = var.getAxisIds().index(axis_id)
            if axis_index == -1:
                raise Exception("Invalid axis cannot perform summation")
        # get axis list to re add axis to var after summation
        axis_list = var.getAxisList()
        axis_list.pop(axis_index)

        # create var
        new_var = genutil.statistics.geometricmean(var, axis_index)
        new_var = cdms2.MV2.asVariable(new_var)

        # add old axis
        for index, axis in enumerate(axis_list):
            new_var.setAxis(index, axis)

        if from_edit_var:
            new_var.id = str(var.id)
        else:
            new_var.id = str(self.name_dialog.textValue())
            get_variables().add_variable(new_var)

        if self.dialog:
            self.dialog.close()
            self.dialog.deleteLater()
        if self.name_dialog is not None:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

        if from_edit_var:
            return new_var

    def launchGeometricMeanDialog(self):
        self.dialog = AxisSelectorDialog()
        self.dialog.accepted.connect(self.getGeometricMeanSuggestedName)
        self.dialog.setWindowTitle('Geometric Mean')
        self.dialog.show()
        self.dialog.raise_()

    def getGeometricMeanSuggestedName(self):
        text = '{0}_geometricmean_over_{1}'.format(self.dialog.getVarName(), self.dialog.getAxis())
        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.geometricMean)

    def launchVarianceDialog(self):
        self.dialog = AxisSelectorDialog()
        self.dialog.accepted.connect(self.getVarianceSuggestedName)
        self.dialog.setWindowTitle('Variance')
        self.dialog.show()
        self.dialog.raise_()

    def getVarianceSuggestedName(self):
        text = '{0}_variance_over_{1}'.format(self.dialog.getVarName(), self.dialog.getAxis())
        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.variance)

    def variance(self):
        var = self.dialog.getVar()
        axis = self.dialog.getAxis()
        axis_index = var.getAxisIndex(axis)

        new_var = var.var(axis_index)

        new_var.id = self.name_dialog.textValue()
        get_variables().add_variable(new_var)

        self.dialog.close()
        self.dialog.deleteLater()

        self.name_dialog.close()
        self.name_dialog.deleteLater()
