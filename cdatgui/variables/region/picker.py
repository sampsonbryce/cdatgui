from PySide import QtGui, QtCore
from genutil import minmax


class ROIPicker(QtGui.QWidget):

    def __init__(self, columns=2, parent=None):
        super(ROIPicker, self).__init__(parent)
        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        self.rois = {}
        self.variable = None

    def set_variable(self, var):
        self.variable = var

    def scan_rois(self, variables):
        self.rois = {}

        for var in variables:
            lat, lon = None, None
            for axis in var.getAxisList():
                if axis.isLatitude():
                    lat = axis
                elif axis.isLongitude():
                    lon = axis
            lat_range = minmax(lat)
            lon_range = minmax(lon)
            roi = (lat_range, lon_range)
            roi_vars = self.rois.get(roi, [])
            roi_vars.append(var)
            self.rois[roi] = roi_vars
