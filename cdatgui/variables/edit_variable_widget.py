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
from roi_selector import ROISelectionDialog
from axes_widgets import QAxisList


class EditVariableDialog(QtGui.QDialog):

    createdVariable = QtCore.Signal(object)
    editedVariable = QtCore.Signal(object)

    def __init__(self, var, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)

        self.var = var
        self.modified = False

        self.setWindowTitle('Edit Variable "%s"' % var.id)
        self.roi = [-180.0, -90.0, 180.0, 90.0]

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
        if self.roi:
            self.roiSelector.setROI(self.roi)

        self.axisList = QAxisList(None, var, self)
        v.addWidget(self.axisList)

        h = QtGui.QHBoxLayout()
        self.selectRoiButton = QtGui.QPushButton('Select Region Of Interest')
        self.selectRoiButton.setDefault(False)
        self.selectRoiButton.setHidden(True)
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

    def set_modified(self, axis):
        self.btnApplyEdits.setEnabled(True)

    def selectRoi(self):
        if self.roi:
            self.roiSelector.setROI(self.roi)
        self.roiSelector.show()

    def setRoi(self):
        self.roi = self.roiSelector.getROI()
        self.updateAxesFromRoi()

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
