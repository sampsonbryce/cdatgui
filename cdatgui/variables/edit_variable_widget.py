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
from cdatgui.variables.manipulations.manipulation import Manipulations


class EditVariableDialog(QtGui.QDialog):

    createdVariable = QtCore.Signal(object)
    editedVariable = QtCore.Signal(object)

    def __init__(self, var, var_list, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.reject)
        self.var = var
        self.var_list = var_list
        self.modified = False

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
        v.addWidget(self.axisList)

        seperator_frame = QtGui.QFrame()
        seperator_frame.setFrameShape(QtGui.QFrame.HLine)
        v.addWidget(seperator_frame)

        self.manipulations = Manipulations()
        self.manipulations.remove.connect(self.removeVar)

        self.manipulations_combo = QtGui.QComboBox()
        for item in ['No Change', 'Summation']:
            self.manipulations_combo.addItem(item)

        self.manipulations_combo.currentIndexChanged.connect(self.manipulateVar)
        v.addWidget(self.manipulations_combo)

        seperator_frame = QtGui.QFrame()
        seperator_frame.setFrameShape(QtGui.QFrame.HLine)
        v.addWidget(seperator_frame)

        h = QtGui.QHBoxLayout()

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

    def manipulateVar(self, index):
        if index != 0:
            self.manipulations.launchSumDialog(self.var)
        self.manipulations_combo.setCurrentIndex(0)

    def removeVar(self, var):
        self.var_list.remove_variable(var)
        self.reject()

    def enableApplySave(self):
        self.btnApplyEdits.setEnabled(True)
        self.btnSaveEditsAs.setEnabled(True)

    def disableApplySave(self):
        self.btnApplyEdits.setEnabled(False)
        self.btnSaveEditsAs.setEnabled(False)

    def set_modified(self, axis):
        self.btnApplyEdits.setEnabled(True)

    def applyEditsClicked(self):
        newvar = self.axisList.var
        newvar.id = self.var.id
        self.editedVariable.emit(newvar)
        self.close()

    def saveEditsAsClicked(self):
        text, ok = QtGui.QInputDialog.getText(self, u"Save Variable As...", u"New Variable Name:")
        if ok:
            newvar = self.axisList.var
            newvar.id = text
            self.createdVariable.emit(newvar)
            self.close()
