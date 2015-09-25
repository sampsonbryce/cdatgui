from PySide import QtGui, QtCore
from cdatgui.bases import RangeWidget
from cdatgui.utils import header_label
from cdatgui.cdat.axis import axis_values, selector_value
import genutil


class AxisBoundsChooser(QtGui.QWidget):
    def __init__(self, axis, parent=None):
        super(AxisBoundsChooser, self).__init__(parent=parent)
        self.axis = axis
        l = QtGui.QVBoxLayout()
        l.addWidget(header_label(axis.id))

        minimum, maximum = (float(num) for num in genutil.minmax(axis))

        bottom = 0
        top = maximum

        self.range = RangeWidget(axis_values(axis))
        l.addWidget(self.range)
        self.setLayout(l)

    def getSelector(self):
        lower, upper = self.range.getBounds()
        lower = selector_value(lower, self.axis)
        upper = selector_value(upper, self.axis)
        return self.axis.id, (lower, upper)