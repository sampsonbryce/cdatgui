from functools import partial

from PySide import QtCore, QtGui
from cdatgui.bases.input_dialog import ValidatingInputDialog, AccessibleButtonDialog
from cdatgui.utils import label
from cdatgui.variables import get_variables
from cdatgui.variables.variable_add import FileNameValidator
import cdutil


class VariableSelectorDialog(AccessibleButtonDialog):
    def __init__(self, prepopulated=False, parent=None):
        super(VariableSelectorDialog, self).__init__(parent=parent)
        self.variable_combo = QtGui.QComboBox()
        self.variable_combo.setModel(get_variables())

        if not prepopulated:
            variable_label = label("Variable:")

            variable_layout = QtGui.QHBoxLayout()
            variable_layout.addWidget(variable_label)
            variable_layout.addWidget(self.variable_combo)

            self.vertical_layout.insertLayout(0, variable_layout)

        self.save_button.setText('Save as')

    def getVarName(self):
        return self.variable_combo.currentText()

    def accept(self):
        self.accepted.emit()


class AxisSelectorDialog(VariableSelectorDialog):
    def __init__(self, prepopulated=False, var=None, parent=None):
        super(AxisSelectorDialog, self).__init__(prepopulated=prepopulated, parent=parent)

        if not prepopulated:
            self.variable_combo.currentIndexChanged.connect(self.changeAxis)
            index = 1
        else:
            if var is None:
                raise Exception('Cannot be prepopulated without providing var')
            self.save_button.setText('Save')
            self.var = var
            self.variable_combo.setCurrentIndex(
                self.variable_combo.findText(get_variables().get_variable_label(self.var)))
            index = 0

        self.axis_combo = QtGui.QComboBox()
        self.vertical_layout.insertWidget(index, self.axis_combo)

        self.populateAxisCombo()

    def changeAxis(self, index):
        for row in range(self.axis_combo.count()):
            self.axis_combo.removeItem(0)
        self.populateAxisCombo()

    def getVar(self):
        return get_variables().get_variable(self.variable_combo.currentText())

    def populateAxisCombo(self):
        for axis in self.getVar().getAxisList():
            self.axis_combo.addItem(axis.id)

    def getAxis(self):
        return str(self.axis_combo.currentText())


class ClimatologyDialog(VariableSelectorDialog):
    def __init__(self, climo_type, parent=None):
        super(ClimatologyDialog, self).__init__(parent=parent)

        self.climo_combo = QtGui.QComboBox()
        if climo_type == 'seasonal':
            self.climo_combo.addItems(['DJF', 'MAM', 'JJA', 'SON', 'YEAR'])
        else:
            self.climo_combo.addItems(
                ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])

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
        bounds = time_axis.getBounds()
        if bounds is not None:
            self.bounds_combo.insertItem(0, 'Original bounds')

        for row in range(self.axis_list.count()):
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

        for ind in self.axis_list.selectedIndexes():
            if ind.data().lower() == self.getVar().getTime().id:
                self.bounds_combo.setEnabled(True)
                return
        self.bounds_combo.setEnabled(False)

    def getVar(self):
        return get_variables().get_variable(self.variable_combo.currentText())

    def getAxis(self):
        selected_axis = []
        for ind in self.axis_list.selectedIndexes():
            for axis in self.getVar().getAxisList():
                if axis.id == ind.data().lower():
                    selected_axis.append(axis.axis)
        return ''.join(selected_axis)

    def getBounds(self):
        return self.bounds_combo.currentText()


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
        text = '{0}_average_over_{1}'.format(self.dialog.getVarName(), self.dialog.getAxis())

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
        self.launchNameDialog(text, self.makeClimatologyVar)

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

    def average(self):
        var_name = self.dialog.getVarName()
        var = get_variables().get_variable(var_name)

        # set all axis to autolevels if isLevel
        for axis in var.getAxisList():
            if axis.isLevel():
                axis.setBounds(axis.genGenericBounds())

        axis = self.dialog.getAxis()
        if 't' in axis:
            time_axis = var.getTime()
            bounds = self.dialog.getBounds()
            if bounds == 'Auto':
                time_axis.setBounds(time_axis.genGenericBounds())
            elif bounds != 'Original bounds':
                self.setBounds(time_axis, bounds)

        new_var = cdutil.averager(var, axis=axis)
        new_var.id = str(self.name_dialog.textValue())
        get_variables().add_variable(new_var)

        self.dialog.close()
        self.dialog.deleteLater()

        self.name_dialog.close()
        self.name_dialog.deleteLater()

    def makeClimatologyVar(self):
        climo = self.dialog.getClimatology()
        var_name = self.dialog.getVarName()
        var = get_variables().get_variable(var_name)
        var = var.var

        if climo in ['DJF', 'MAM', 'JJA', 'SON', 'ANN']:
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

    def launchSumDialog(self, var=None):
        if var is None:
            self.dialog = AxisSelectorDialog()
            self.dialog.accepted.connect(self.getSumSuggestedName)
        else:
            self.dialog = AxisSelectorDialog(prepopulated=True, var=var)
            self.dialog.accepted.connect(partial(self.sum, True))

        self.dialog.setWindowTitle('Summation')
        self.dialog.show()
        self.dialog.raise_()

    def launchSTDDialog(self, var=None):
        if var is None:
            self.dialog = AxisSelectorDialog()
            self.dialog.accepted.connect(self.getSTDSuggestedName)
        else:
            self.dialog = AxisSelectorDialog(prepopulated=True, var=var)
            self.dialog.accepted.connect(partial(self.std, True))
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

    def sum(self, replace=False):
        var = self.dialog.getVar()
        axis = self.dialog.getAxis()
        axis_index = var.getAxisIndex(axis)
        if axis_index == -1:
            raise Exception("Invalid axis cannot perform summation")

        new_var = var.sum(axis_index)

        if replace:
            new_var.id = var.id
            self.remove.emit(var)
        else:
            new_var.id = self.name_dialog.textValue()

        get_variables().add_variable(new_var)

        self.dialog.close()
        self.dialog.deleteLater()

        if self.name_dialog is not None:
            self.name_dialog.close()
            self.name_dialog.deleteLater()

    def getSTDSuggestedName(self):
        text = '{0}_std_over_{1}'.format(self.dialog.getVarName(), self.dialog.getAxis())
        text = self.adjustNameForDuplicates(text)
        self.launchNameDialog(text, self.std)

    def std(self, replace=False):
        var = self.dialog.getVar()
        axis = self.dialog.getAxis()
        axis_index = var.getAxisIndex(axis)
        if axis_index == -1:
            raise Exception("Invalid axis cannot perform summation")

        new_var = var.std(axis_index)

        if replace:
            new_var.id = var.id
            self.remove.emit(var)
        else:
            new_var.id = self.name_dialog.textValue()

        get_variables().add_variable(new_var)

        self.dialog.close()
        self.dialog.deleteLater()

        if self.name_dialog is not None:
            self.name_dialog.close()
            self.name_dialog.deleteLater()
