
from PySide import QtGui, QtCore
import numpy
import cdms2
from axis_bounds import AxisBoundsChooser
from cdatgui.utils import label, header_label


class QAxisList(QtGui.QWidget):
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

    def getVar(self):
        return self._var

    def setVar(self, var):
        """ Iterate through the variable's axes and create and initialize an Axis
        object for each axis.
        """

        self.clear()
        self._var = var

        if var is None:
            return

        for axis in var.getAxisList():
            w = AxisBoundsChooser(axis)
            self.axisWidgets.append(w)
            self.vbox.addWidget(w)

    var = property(getVar, setVar)
