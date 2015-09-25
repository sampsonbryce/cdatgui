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
    def __init__(self, var, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)

        self.var = var
        self.modified = False

        self.setWindowTitle('Edit Variable "%s"' % var.id)
        self.roi = [ -180.0, -90.0, 180.0, 90.0 ]

        self.ask = QtGui.QInputDialog()
        self.ask.setWindowModality(QtCore.Qt.WindowModal)
        self.ask.setLabelText("This variable already exists!\nPlease change its name below and click ok to replace it.\n")

        self.axisListHolder = None

        v = QtGui.QVBoxLayout()
        self.resize(QtCore.QSize(800,600))
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

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

        h=QtGui.QHBoxLayout()
        self.selectRoiButton = QtGui.QPushButton('Select Region Of Interest (ROI)')
        self.selectRoiButton.setDefault(False)
        self.selectRoiButton.setHidden(True)
        h.addWidget(self.selectRoiButton)

        s=QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
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

        self.layout = v
        self.setLayout(v)

        self.axisList = QAxisList(None, var, self)
        self.axisList.setupVariableAxes()
        self.axisListHolder = axisList
        self.fillDimensionsWidget(axisList)
        self.updateVarInfo(axisList)

        self.connectSignals()

    def closeEvent(self, event):
        pass

    def connectSignals(self):
        self.btnCancel.clicked.connect(self.close)
        self.connect(self.ask,
                     QtCore.SIGNAL('accepted()'),
                     self.checkTargetVarName)

        ## Define button
        self.btnApplyEdits.clicked.connect(self.applyEditsClicked)
        self.btnSaveEditsAs.clicked.connect(self.saveEditsAsClicked)
        self.selectRoiButton.clicked.connect(self.selectRoi)

    def selectRoi( self ):
        if self.roi:
            self.roiSelector.setROI( self.roi )
        self.roiSelector.show()

    def setRoi(self):
        self.roi = self.roiSelector.getROI()
        self.updateAxesFromRoi()

    def updateAxesFromRoi(self):
        from CDMS_variable_readers import getAxisType, AxisType
        #print "Selected roi: %s " % str( self.roi )
        # Add code here to update Lat Lon sliders.
        n = self.axisListHolder.gridLayout.rowCount()
        #print "ok in roi self is: ",n
        for i in range(len(self.axisListHolder.axisWidgets)):
            axis = self.axisListHolder.axisWidgets[i]
            axis_type = getAxisType( axis.axis )
            if ( axis_type == AxisType.Latitude ) or axis.virtual==1:
                # Ok this is a lat we need to adjust the sliders now.
                lat1 = self.roi[1]
                lat2 = self.roi[3]
                [ lat1, lat2 ] = axis.sliderCombo.checkBounds( [ lat1, lat2 ], axis.axis.parent )
                axis.sliderCombo.updateTopSlider(axis.sliderCombo.findAxisIndex(lat1))
                axis.sliderCombo.updateBottomSlider(axis.sliderCombo.findAxisIndex(lat2))
            if ( axis_type == AxisType.Longitude ) or axis.virtual==1:
                # Ok this is a lat we need to adjust the sliders now.
                lon1 = self.roi[0]
                lon2 = self.roi[2]
                [ lon1, lon2 ] = axis.sliderCombo.checkBounds( [ lon1, lon2 ], axis.axis.parent )
                axis.sliderCombo.updateTopSlider(axis.sliderCombo.findAxisIndex(lon1))
                axis.sliderCombo.updateBottomSlider(axis.sliderCombo.findAxisIndex(lon2))

    def openSelectFileDialog(self):
        file = QtGui.QFileDialog.getOpenFileName(self, 'Open CDAT data file...',
                                                 '',
                                                 'All files (*.*)')
                                                 # VariableProperties.FILTER + ';;All files (*.*)')
        if not file.isNull():
            self.setFileName(file)

    def setFileName(self,fnm):
        self.fileEdit.setText(fnm)
        self.updateFile()

    def updateFileFromReturnPressed(self):
        self.updatingFile = True
        self.updateFile()

    def updateVariableList(self):
        # Add Axis List
        count = self.varCombo.count()
        self.varCombo.insertSeparator(count)
        self.varCombo.model().item(count, 0).setText('AXIS LIST')
        for axis in self.cdmsFile.axes.itervalues():
            axisName = axis.id + " (" + str(len(axis)) + ") - [" + axis.units + ":  (" + str(axis[0]) + ", " + str(axis[-1]) + ")]"
            self.varCombo.addItem(axisName, QtCore.QVariant(QtCore.QStringList(['axes', axis.id])))

        # By default, select first var
        self.varCombo.setCurrentIndex(1)

        # manually call this since we listen for activated now
        self.variableSelected(self.varCombo.itemText(1))

    def clearDimensionsWidget(self):
        if not self.axisListHolder is None:
            self.axisListHolder.destroy()
        it = self.dimsLayout.takeAt(0)
        if it:
            it.widget().deleteLater()
            del(it)

    def fillDimensionsWidget(self, axisList):
        self.clearDimensionsWidget()
        self.axisListHolder = axisList
        self.dimsLayout.insertWidget(0, axisList)
        self.updateVarInfo(axisList)
        self.dims.update()
        self.update()

    def updateVarInfo(self, axisList):
        from CDMS_variable_readers import getAxisType, AxisType

        """ Update the text box with the variable's information """
        if axisList is None:
            return

        var = axisList.getVar()
        showRoi = False
        for i in range(len(self.axisListHolder.axisWidgets)):
            axis = self.axisListHolder.axisWidgets[i]
            axis_type = getAxisType(axis.axis)
            if axis_type in [ AxisType.Latitude, AxisType.Longitude ] or axis.virtual == 1:
                showRoi = True
        if showRoi:
            self.selectRoiButton.setHidden(False)
        else:
            self.selectRoiButton.setHidden(True)

    def getUpdatedVar(self, targetId):
        new_var = self.var(**self.axisList.getKwargs())
        new_var.id = targetId
        return new_var

    def applyEditsClicked(self):
        # TODO: Update current variable
        pass

    def saveEditsAsClicked(self):
        # TODO: copy to new variable
        pass

    def modifiedOn(self):
        txt = str(self.title.text())
        if txt.find("(Modified)")>-1:
            return
        else:
            self.title.setText("%s (Modified)" % txt)
