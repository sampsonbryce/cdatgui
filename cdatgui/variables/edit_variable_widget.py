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

        axisList = QAxisList(None, var, self)
        axisList.setupVariableAxes()
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

    def checkTargetVarName(self):
        result = None
        while result is None:
            result = self.ask.result()
            value = self.ask.textValue()
        if result == 1: # make sure we pressed Ok and not Cancel
            if str(value) != self.checkAgainst:
                self.getUpdatedVarCheck(str(value))
            else:
                self.getUpdatedVar(str(value))

    def selectRoi( self ):
        if self.roi: self.roiSelector.setROI( self.roi )
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
    ##             it.widget().destroy()
#            self.dimsLayout.removeItem(it)
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

    def getUpdatedVarCheck(self, targetId=None):
        """ Return a new tvariable object with the updated information from
        evaluating the var with the current user selected args / options
        """
        axisList = self.dimsLayout.itemAt(0).widget()

        if targetId is not None:
            tid = targetId
        elif axisList.cdmsFile is None:
            tid = axisList.var.id
        else:
            tid = axisList.var

        exists = False
        for it in self.root.dockVariable.widget().getItems(project=False):
            if tid == str(it.text()).split()[1]:
                exists = True
        ## Ok at that point we need to figure out if
        if exists:
            self.checkAgainst = tid
            self.ask.setTextValue(tid)
            self.ask.show()
            self.ask.exec_()
        else:
            self.getUpdatedVar(tid)

    def getUpdatedVar(self, targetId):
        axisList = self.dimsLayout.itemAt(0).widget()
        kwargs = self.generateKwArgs()
        # Here we try to remove useless keywords as we record them
        cmds = ""
        for k in kwargs:
            if k=='order':
                o = kwargs[k]
                skip = True
                for i in range(len(o)):
                    if int(o[i])!=i:
                        skip = False
                        break
                if skip:
                    continue
            cmds += "%s=%s," % (k, repr(kwargs[k]))
        cmds = cmds[:-1]
#        uvar=axisList.getVar()
#        if isinstance(uvar,cdms2.axis.FileAxis):
#            updatedVar = cdms2.MV2.array(uvar)
#        else:
#            updatedVar = uvar(**kwargs)

        # Get the variable after carrying out the: def, sum, avg... operations
#        updatedVar = axisList.execAxesOperations(updatedVar)
        updatedVar = axisList.getVar()

        if axisList.cdmsFile is None:
            oid = updatedVar.id
        else:
            oid = "cdmsFileVariable"
        ## Squeeze?
        if updatedVar.rank() !=0:
            if self.root.preferences.squeeze.isChecked():
                #updatedVar=updatedVar(squeeze=1)
                self.root.record("%s = %s(squeeze=1)" % (targetId,targetId))
                kwargs['squeeze']=1
        else:
            val = QtGui.QMessageBox()
            val.setText("%s = %f" % (updatedVar.id,float(updatedVar)))
            val.exec_()




        # Send information to controller so the Variable can be reconstructed
        # later. The best way is by emitting a signal to be processed by the
        # main window. When this panel becomes a global panel, then we will do
        # that. For now I will talk to the main window directly.

        #_app = get_vistrails_application()
        #controller = _app.uvcdatWindow.get_current_project_controller()
        def get_kwargs_str(kwargs_dict):
            kwargs_str = ""
            for k, v in kwargs_dict.iteritems():
                if k == 'order':
                    o = kwargs_dict[k]
                    skip = True
                    for i in range(len(o)):
                        if int(o[i])!=i:
                            skip = False
                            break
                    if skip:
                        continue
                kwargs_str += "%s=%s," % (k, repr(v))
            return kwargs_str
        axes_ops_dict = axisList.getAxesOperations()
        url = None
        if hasattr(self.cdmsFile, "uri"):
            url = self.cdmsFile.uri
        cdmsVar = None
        # TODO apply axes to variable here
        # if not computed_var:
        #     cdmsVar = CDMSVariable(filename=self.cdmsFile.id, url=url, name=targetId,
        #                            varNameInFile=original_id,
        #                            axes=get_kwargs_str(kwargs),
        #                            axesOperations=str(axes_ops_dict))
        #     controller.add_defined_variable(cdmsVar)
        # else:
        #     controller.copy_computed_variable(original_id, targetId,
        #                                       axes=get_kwargs_str(kwargs),
        #                                       axesOperations=str(axes_ops_dict))

        #updatedVar = controller.create_exec_new_variable_pipeline(targetId)

##        if updatedVar is None:
#            return axisList.getVar()

#        self.emit(QtCore.SIGNAL('definedVariableEvent'),updatedVar)

        # if(self.varEditArea.widget()):
        #     self.varEditArea.widget().var = updatedVar
        #     axisList.setVar(updatedVar)

        # self.updateVarInfo(axisList)
        # return updatedVar

    def generateKwArgs(self, axisList=None):
        """ Generate and return the variable axes keyword arguments """
        if axisList is None:
            axisList = self.dimsLayout.itemAt(0).widget()

        kwargs = {}
        for axisWidget in axisList.getAxisWidgets():
            if not axisWidget.isHidden():
                kwargs[axisWidget.axis.id] = axisWidget.getCurrentValues()

        # Generate additional args
        #kwargs['squeeze'] = 0
        kwargs['order'] = axisList.getAxesOrderString()
        return kwargs

    def applyEditsClicked(self):
        varname = self.varEditArea.widget().var.id
        self.getUpdatedVar(varname)

        #controller.variableEdited(varname)

    def saveEditsAsClicked(self):
        # TODO: copy to new variable
        pass

    def modifiedOn(self):
        txt = str(self.title.text())
        if txt.find("(Modified)")>-1:
            return
        else:
            self.title.setText("%s (Modified)" % txt)
