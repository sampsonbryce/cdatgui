
from PySide import QtGui, QtCore
from axis_bounds import AxisBoundsChooser
from cdatgui.utils import header_label


class QAxisList(QtGui.QWidget):
    axisEdited = QtCore.Signal(object)
    """ Widget containing a list of axis widgets for the selected variable """

    def __init__(self, cdmsFile=None, var=None, parent=None):
        super(QAxisList, self).__init__(parent)
        self.axisWidgets = []  # List of QAxis widgets
        self.cdmsFile = cdmsFile  # cdms file associated with the variable
        self._var = None

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

    def getROI(self):
        if self._var is None:
            return

        for w in self.axisWidgets:
            if w.axis.isLatitude():
                lat_bot, lat_top = w.getBotTop()
            if w.axis.isLongitude():
                lon_bot, lon_top = w.getBotTop()

        return (lat_bot, lat_top), (lon_bot, lon_top)

    def setROI(self, latitude=None, longitude=None):
        if latitude is not None and self.latitude is not None:
            self.latitude.setBotTop(*latitude)
        if longitude is not None and self.longitude is not None:
            self.longitude.setBotTop(*longitude)

    def getVar(self):
        return self._var.get_original()(**self.getKwargs())

    def setVar(self, var):
        """ Iterate through the variable's axes and create and initialize an Axis
        object for each axis.
        """

        self.clear()
        self._var = var

        if var is None:
            return

        orig = var.get_original()
        var_axes = {ax.id: ax for ax in var.getAxisList()}

        for axis in orig.getAxisList():
            w = AxisBoundsChooser(var_axes[axis.id], source_axis=axis)
            if axis.isLatitude():
                self.latitude = w
            if axis.isLongitude():
                self.longitude = w
            w.boundsEdited.connect(self.axisEdited.emit)
            self.axisWidgets.append(w)
            self.vbox.addWidget(w)

    var = property(getVar, setVar)
