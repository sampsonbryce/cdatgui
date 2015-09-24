from PySide import QtGui, QtCore
from cdatgui.bases import RangeWidget
from cdatgui.utils import header_label
from cdatgui.cdat import format_axis, parse_axis
import genutils


class AxisBoundsChooser(QtGui.QWidget):
    def __init__(self, axis, parent=None):
        super(AxisBoundsChooser, self).__init__(parent=parent)
        self.axis = axis
        l = QtGui.QVBoxLayout()
        l.addWidget(header_label(axis.id))

        minimum, maximum = (float(num) for num in genutils.minmax(axis))

        bottom = 0
        top = maximum

        self.range = RangeWidget(minimum, maximum, bottom, top,
                                 formatter=format_axis(axis),
                                 parser=parse_axis(axis))
        l.addWidget(self.range)
        self.setLayout(l)
