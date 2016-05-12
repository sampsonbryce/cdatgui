from functools import partial

from PySide import QtCore, QtGui
from cdatgui.bases.input_dialog import ValidatingInputDialog, AccessableButtonDialog
from cdatgui.utils import label
from cdatgui.variables import get_variables
from cdatgui.variables.variable_add import FileNameValidator
import cdutil


class ClimatologyDialog(AccessableButtonDialog):
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

    def getVarName(self):
        return self.variable_combo.currentText()

    def getBounds(self):
        return self.bounds_combo.currentText()

    def accept(self):
        self.accepted.emit()


class RegridDialog(AccessableButtonDialog):
    def __init__(self, parent=None):
        super(RegridDialog, self).__init__(parent=parent)

        self.variable_combo = QtGui.QComboBox()
        self.variable_combo.setModel(get_variables())

        variable_label = label("Variable:")

        variable_layout = QtGui.QHBoxLayout()
        variable_layout.addWidget(variable_label)
        variable_layout.addWidget(self.variable_combo)

        self.source_grid_combo = QtGui.QComboBox()
        for v_label, var in get_variables().values:
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

        regrid_method_label = label("Regrid Method:")

        regrid_method_layout = QtGui.QHBoxLayout()
        regrid_method_layout.addWidget(regrid_method_label)
        regrid_method_layout.addWidget(self.regrid_method_combo)

        self.regrid_method_widget = QtGui.QWidget()
        self.regrid_method_widget.setLayout(regrid_method_layout)
        self.regrid_method_widget.hide()

        self.vertical_layout.insertLayout(0, variable_layout)
        self.vertical_layout.insertLayout(1, source_grid_layout)
        self.vertical_layout.insertLayout(2, regrid_tool_layout)

        self.save_button.setText('Save as')

    def updateRegridMethod(self, index):
        if self.regrid_tool_combo.currentText() == 'esmf':
            self.vertical_layout.insertWidget(3, self.regrid_method_widget)
            self.regrid_method_widget.show()
        else:
            if self.regrid_method_widget.isVisible():
                self.vertical_layout.takeAt(3)
                self.regrid_method_widget.hide()

    def getVarName(self):
        return self.variable_combo.currentText()

    def getSourceVarName(self):
        return self.source_grid_combo.currentText().split(" ")[0]

    def getRegridTool(self):
        return self.regrid_tool_combo.currentText()

    def getRegridMethod(self):
        if self.regrid_method_widget.isVisible():
            return self.regrid_method_combo.currentText()
        return None

    def accept(self):
        self.accepted.emit()


class Manipulations(object):
    def __init__(self):
        super(Manipulations, self).__init__()
        self.dialog = None
        self.name_dialog = None

    def launchRegridDialog(self):
        self.dialog = RegridDialog()
        self.dialog.accepted.connect(self.getRegridSuggestedName)
        self.dialog.rejected.connect(self.dialog.deleteLater)
        self.dialog.show()
        self.dialog.raise_()

    def getRegridSuggestedName(self):
        text = '{0}_regrid_from_{1}_{2}'.format(self.dialog.getVarName(), self.dialog.getSourceVarName(), self.dialog.getRegridTool())
        if self.dialog.getRegridMethod():
            text += '_' + str(self.dialog.getRegridMethod())

        count = 1
        while get_variables().variable_exists(text):
            if count == 1:
                text = text + '_' + str(count)
            else:
                text = text[:-2] + '_' + str(count)
            count += 1

        self.launchNameDialog(text, self.regrid)

    def regrid(self):
        var_name = self.dialog.getVarName()
        var = get_variables().get_variable(var_name)
        source_var_name = self.dialog.getSourceVarName()
        source_var = get_variables().get_variable(source_var_name)
        regrid_tool = self.dialog.getRegridTool()
        kargs = {}
        kargs['regrid_tool'] = regrid_tool
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

    def launchAverageDialog(self):
        pass

    def average(self):
        pass

    def launchClimatologyDialog(self, ctype):
        self.dialog = ClimatologyDialog(ctype)
        self.dialog.accepted.connect(partial(self.getClimoSuggestedName, ctype))
        self.dialog.rejected.connect(self.dialog.deleteLater)
        self.dialog.setMinimumSize(300, 200)
        self.dialog.show()
        self.dialog.raise_()

    def getClimoSuggestedName(self, ctype):
        if ctype == 'seasonal':
            text = '{0}_{1}_{2}_climatology'.format(self.dialog.getClimatology(), self.dialog.getBounds().lower(),
                                                    self.dialog.getVarName())
        else:
            text = '{0}_{1}_climatology'.format(self.dialog.getClimatology(), self.dialog.getVarName())

        count = 1
        while get_variables().variable_exists(text):
            if count == 1:
                text = text + '_' + str(count)
            else:
                text = text[:-2] + '_' + str(count)
            count += 1

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

    def makeClimatologyVar(self):
        climo = self.dialog.getClimatology()
        var_name = self.dialog.getVarName()
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
