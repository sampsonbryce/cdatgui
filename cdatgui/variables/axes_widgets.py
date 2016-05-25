from PySide import QtGui, QtCore
from axis_bounds import AxisBoundsChooser
from cdatgui.utils import header_label
from region import ROIPreview


class QAxisList(QtGui.QWidget):
    axisEdited = QtCore.Signal(object)
    manipulationComboIndexesChanged = QtCore.Signal()
    validParams = QtCore.Signal()
    invalidParams = QtCore.Signal()

    """ Widget containing a list of axis widgets for the selected variable """

    def __init__(self, cdmsFile=None, var=None, parent=None):
        super(QAxisList, self).__init__(parent)
        self.axisWidgets = []  # List of QAxis widgets
        self.cdmsFile = cdmsFile  # cdms file associated with the variable
        self._var = None
        self.squeeze = True

        self.manipulation_combos = []

        # Init & set the layout
        self.vbox = QtGui.QVBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(header_label("Dimensions"))
        vbox.addLayout(self.vbox)
        vbox.addStretch()
        vbox.setSpacing(0)
        vbox.setContentsMargins(5, 5, 5, 5)
        self.setLayout(vbox)

        self.latitude = None
        self.longitude = None
        self.roi_vbox = QtGui.QVBoxLayout()
        self.roi_layout = QtGui.QHBoxLayout()
        self.roi_layout.addLayout(self.roi_vbox)

        roi_preview = QtGui.QVBoxLayout()
        # keep this proportional
        self.roi_sample = ROIPreview((500, 500))
        roi_preview.addWidget(self.roi_sample)
        vbox.addLayout(roi_preview)
        vbox.addLayout(self.roi_layout)

        success = vbox.setAlignment(roi_preview, QtCore.Qt.AlignCenter)
        self.roi_vbox.setAlignment(QtCore.Qt.AlignCenter)
        self.var = var

    def clear(self):
        """ Remove the QAxis widgets, empty axisWidgets and axesNames lists from
        the grid layout
        """
        for widget in self.axisWidgets:
            widget.deleteLater()
        self.axisWidgets = []

    def getKwargs(self):
        kwargs = {}
        for widget in self.axisWidgets:
            key, bounds = widget.getSelector()
            kwargs[key] = bounds
        if self.squeeze:
            kwargs['squeeze'] = True
        return kwargs

    def getLatLon(self):
        if self._var is None:
            return None, None
        lat_ax = None
        lon_ax = None
        for axis in self._var.getAxisList():
            if axis.isLatitude():
                lat_ax = axis
            if axis.isLongitude():
                lon_ax = axis
        return lat_ax, lon_ax

    def updateROI(self, axis):
        min_lat, max_lat = self.latitude.getBotTop()
        min_lon, max_lon = self.longitude.getBotTop()
        self.roi_sample.setLatRange(min_lat, max_lat, self.latitude.range.flipped)
        self.roi_sample.setLonRange(min_lon, max_lon, self.longitude.range.flipped)

    def getVar(self):
        orig = self._var.get_original()
        new_var = orig(**self.getKwargs())
        return new_var

    def setVar(self, var):
        """ Iterate through the variable's axes and create and initialize an Axis
        object for each axis.
        """

        self.clear()
        self._var = var
        latitude_layout = None
        longitude_layout = None

        if var is None:
            return

        orig = var.get_original()
        var_axes = {ax.id: ax for ax in var.getAxisList()}

        for axis in orig.getAxisList():
            if axis.id in var_axes:
                w = AxisBoundsChooser(var_axes[axis.id], source_axis=axis)
                # add manipulations
                manipulations_combo = QtGui.QComboBox()
                manipulations_combo.currentIndexChanged.connect(lambda y: self.manipulationComboIndexesChanged.emit())
                self.manipulation_combos.append((axis.id, manipulations_combo))

                for item in ['Default', 'Summation', 'Average', 'Standard Deviation', 'Geometric Mean']:
                    manipulations_combo.addItem(item)

                axis_bounds_layout = QtGui.QHBoxLayout()
                axis_bounds_layout.addWidget(manipulations_combo)
                axis_bounds_layout.addWidget(w)
                w.validParams.connect(self.validParams.emit)
                w.invalidParams.connect(self.invalidParams.emit)
                if axis.isLatitude():
                    self.latitude = w
                    latitude_layout = axis_bounds_layout
                elif axis.isLongitude():
                    self.longitude = w
                    longitude_layout = axis_bounds_layout
                    if axis.isCircular():
                        self.roi_sample.setCircular(True)
                else:
                    self.vbox.addLayout(axis_bounds_layout)
                w.boundsEdited.connect(self.axisEdited.emit)
                self.axisWidgets.append(w)

        if self.latitude is not None:
            if self.longitude is not None:
                self.roi_vbox.addLayout(latitude_layout)
                self.roi_vbox.addLayout(longitude_layout)
                self.layout().addLayout(self.roi_layout)
                self.latitude.boundsEdited.connect(self.updateROI)
                self.longitude.boundsEdited.connect(self.updateROI)
                self.latitude.boundsEdited.emit(10)  # dummy var to set initial values
                self.longitude.boundsEdited.emit(10)
            else:
                self.layout().addLayout(latitude_layout)
        elif self.longitude is not None:
            self.layout().addLayout(longitude_layout)

    var = property(getVar, setVar)
