###############################################################################
#                                                                             #
# Module:       variable editor module                                        #
#                                                                             #
# Copyright:    "See file Legal.htm for copyright information."               #
#                                                                             #
# Authors:      PCMDI Software Team                                           #
#               Lawrence Livermore National Laboratory:                       #
#               website: http://uv-cdat.llnl.gov/                             #
#                                                                             #
# Description:  UV-CDAT GUI variable editor.                                  #
#                                                                             #
# Version:      6.0                                                           #
#                                                                             #
###############################################################################
from PySide import QtCore, QtGui

from axes_widgets import QAxisList
from cdatgui.utils import label
from cdatgui.variables.manipulations.manipulation import Manipulations


class EditVariableDialog(QtGui.QDialog):
    createdVariable = QtCore.Signal(object)
    editedVariable = QtCore.Signal(object)

    def __init__(self, var, var_list, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.reject)
        self.valid = True
        self.var = var
        self.var_list = var_list
        self.modified = False
        self.manipulations = Manipulations()
        self.manipulations.remove.connect(self.removeVar)

        self.setWindowTitle('Edit Variable "%s"' % var.id)

        v = QtGui.QVBoxLayout()
        self.resize(QtCore.QSize(800, 600))
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

        self.dims = QtGui.QFrame()
        self.dimsLayout = QtGui.QVBoxLayout()
        self.dims.setLayout(self.dimsLayout)
        v.addWidget(self.dims)

        self.axisList = QAxisList(None, var, self)
        self.axisList.invalidParams.connect(self.disableApplySave)
        self.axisList.validParams.connect(self.enableApplySave)
        self.axisList.manipulationComboIndexesChanged.connect(
            lambda: self.enableApplySave() if self.valid else self.disableApplySave())
        v.addWidget(self.axisList)

        h = QtGui.QHBoxLayout()

        squeeze_label = label('Squeeze')
        squeeze_check = QtGui.QCheckBox()
        squeeze_check.setChecked(True)
        squeeze_check.stateChanged.connect(self.setSqueeze)
        squeeze_layout = QtGui.QHBoxLayout()
        squeeze_layout.addWidget(squeeze_label)
        squeeze_layout.addWidget(squeeze_check)
        h.addLayout(squeeze_layout)

        s = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                              QtGui.QSizePolicy.Preferred)
        h.addItem(s)

        self.btnApplyEdits = QtGui.QPushButton("Apply")
        self.btnApplyEdits.setEnabled(False)
        h.addWidget(self.btnApplyEdits)

        self.btnSaveEditsAs = QtGui.QPushButton("Save As")
        h.addWidget(self.btnSaveEditsAs)

        self.btnCancel = QtGui.QPushButton("Close")
        h.addWidget(self.btnCancel)

        v.addLayout(h)

        self.setLayout(v)

        self.btnCancel.clicked.connect(self.close)
        # Define button
        self.btnApplyEdits.clicked.connect(self.applyEditsClicked)
        self.btnSaveEditsAs.clicked.connect(self.saveEditsAsClicked)
        self.axisList.axisEdited.connect(self.set_modified)

    def setSqueeze(self, state):
        if state == QtCore.Qt.Checked:
            self.axisList.squeeze = True
        elif state == QtCore.Qt.Unchecked:
            self.axisList.squeeze = False
        self.set_modified()

    def removeVar(self, var):
        self.var_list.remove_variable(var)
        self.reject()

    def enableApplySave(self):
        self.valid = True
        self.btnApplyEdits.setEnabled(True)
        self.btnSaveEditsAs.setEnabled(True)

    def disableApplySave(self):
        self.valid = False
        self.btnApplyEdits.setEnabled(False)
        self.btnSaveEditsAs.setEnabled(False)

    def set_modified(self, axis=None):
        self.btnApplyEdits.setEnabled(True)

    def applyEditsClicked(self):
        newvar = self.axisList.var
        newvar = self.applyManipulations(newvar)
        newvar.id = self.var.id
        self.editedVariable.emit(newvar)
        self.close()

    def applyManipulations(self, var):
        new_var = var
        for axis_id, combo in self.axisList.manipulation_combos:
            manipulation = combo.currentText()
            if manipulation == 'Summation':
                new_var = self.manipulations.sum(new_var, axis_id)
            elif manipulation == 'Standard Deviation':
                new_var = self.manipulations.std(new_var, axis_id)
            elif manipulation == 'Geometric Mean':
                new_var = self.manipulations.geometricMean(new_var, axis_id)
            elif manipulation == 'Average':
                new_var = self.manipulations.average(new_var, axis_id)

        return new_var

    def saveEditsAsClicked(self):
        text, ok = QtGui.QInputDialog.getText(self, u"Save Variable As...", u"New Variable Name:")
        if ok:
            newvar = self.axisList.var
            newvar.id = text
            self.createdVariable.emit(newvar)
            self.close()
