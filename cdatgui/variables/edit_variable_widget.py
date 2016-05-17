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
from region import ROISelectionDialog
from axes_widgets import QAxisList


class EditVariableDialog(QtGui.QDialog):

    createdVariable = QtCore.Signal(object)
    editedVariable = QtCore.Signal(object)

    def __init__(self, var, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.reject)

        self.var = var
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

        self.roiSelector = ROISelectionDialog(self)
        self.roiSelector.setWindowFlags(self.roiSelector.windowFlags() |
                                        QtCore.Qt.WindowStaysOnTopHint)
        self.roiSelector.doneConfigure.connect(self.setRoi)

        self.axisList = QAxisList(None, var, self)
        self.axisList.invalidParams.connect(self.disableApplySave)
        self.axisList.validParams.connect(self.enableApplySave)
        v.addWidget(self.axisList)

        h = QtGui.QHBoxLayout()
        self.selectRoiButton = QtGui.QPushButton('Select Region Of Interest')
        self.selectRoiButton.setDefault(False)
        self.selectRoiButton.setHidden(True)
        for axis in self.var.getAxisList():
            if axis.isLatitude() or axis.isLongitude():
                self.selectRoiButton.setHidden(False)
                break

        h.addWidget(self.selectRoiButton)

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
        self.selectRoiButton.clicked.connect(self.selectRoi)
        self.axisList.axisEdited.connect(self.set_modified)

    def enableApplySave(self):
        self.btnApplyEdits.setEnabled(True)
        self.btnSaveEditsAs.setEnabled(True)

    def disableApplySave(self):
        self.btnApplyEdits.setEnabled(False)
        self.btnSaveEditsAs.setEnabled(False)

    def set_modified(self, axis):
        self.btnApplyEdits.setEnabled(True)

    def selectRoi(self):
        (lat0, lat1), (lon0, lon1) = self.axisList.getROI()
        self.roiSelector.setROI((lon0, lat0, lon1, lat1))
        self.roiSelector.show()

    def setRoi(self):
        roi = self.roiSelector.getROI()
        lon0, lat0, lon1, lat1 = roi
        self.axisList.setROI((lat0, lat1), (lon0, lon1))

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
