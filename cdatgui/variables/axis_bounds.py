from PySide import QtGui, QtCore

import numpy

from cdatgui.bases import RangeWidget
from cdatgui.utils import header_label
from cdatgui.cdat.axis import axis_values, selector_value, format_degrees, format_time_axis, parse_degrees, format_axis
from functools import partial
import genutil


class AxisBoundsChooser(QtGui.QWidget):
    boundsEdited = QtCore.Signal(object)
    validParams = QtCore.Signal()
    invalidParams = QtCore.Signal()

    def __init__(self, axis, source_axis=None, parent=None):
        super(AxisBoundsChooser, self).__init__(parent=parent)
        if source_axis is not None:
            self.axis = source_axis
        else:
            self.axis = axis
        if all(earlier >= later for earlier, later in zip(axis, axis[1:])):
            flipped = True
        else:
            flipped = False
        l = QtGui.QVBoxLayout()
        l.addWidget(header_label(axis.id))

        if source_axis is not None:
            self.values = [val for val in source_axis]

            minimum, maximum = (float(num) for num in genutil.minmax(source_axis))
            bottom, top = (float(num) for num in genutil.minmax(axis))

            # adjust size for circular behavior
            if source_axis.isCircular():
                diff = self.values[-1] - self.values[-2]
                for i in range(len(self.values) / 2):
                    self.values.insert(0, self.values[0] - diff)
                    self.values.append(self.values[-1] + diff)

                formatted_vals = []
                for val in self.values:
                    formatted_vals.append(format_degrees(val))

                for i, v in enumerate(self.values):
                    if v == bottom:
                        bot_ind = i
                    if v == top:
                        top_ind = i
                if flipped:
                    tmp = bot_ind
                    bot_ind = top_ind
                    top_ind = tmp

                self.range = RangeWidget(formatted_vals, bottom=bot_ind, top=top_ind, axis_type=source_axis.id,
                                         flipped=flipped)
            else:
                for i, v in enumerate(self.values):
                    if v == bottom:
                        bot_ind = i
                    if v == top:
                        top_ind = i
                if flipped:
                    tmp = bot_ind
                    bot_ind = top_ind
                    top_ind = tmp

                formatter = format_axis(axis)
                values = []
                for value in self.values:
                    values.append(formatter(value))

                self.range = RangeWidget(values, bottom=bot_ind, top=top_ind,
                                         axis_type=source_axis.id, flipped=flipped)
        else:
            minimum, maximum = (float(num) for num in genutil.minmax(axis))
            self.range = RangeWidget(axis_values(axis))

        self.range.validParams.connect(self.validParams.emit)
        self.range.invalidParams.connect(self.invalidParams.emit)

        l.addWidget(self.range)
        self.setLayout(l)

        emitter = partial(self.boundsEdited.emit, self.axis)

        self.range.boundsEdited.connect(emitter)

    def getMinMax(self):
        indices = self.range.getBounds()
        values = [self.values[index] for index in indices]
        return values

    def getBotTop(self):
        indices = self.range.getBounds()
        values = [self.values[index] for index in indices]
        return values

    def setBotTop(self, bottom, top):
        # Round bottom and top to actual values
        min_lower_diff = None
        min_upper_diff = None
        lower_ind, upper_ind = None, None
        for ind, val in enumerate(self.axis):
            low_diff = abs(bottom - val)
            up_diff = abs(top - val)
            if min_lower_diff is None or min_lower_diff >= low_diff:
                lower_ind = ind
                min_lower_diff = low_diff
            if min_upper_diff is None or min_upper_diff >= up_diff:
                upper_ind = ind
                min_upper_diff = up_diff

        self.range.setBounds(lower_ind, upper_ind)

    def getSelector(self):
        bound1, bound2 = self.range.getBounds()
        if self.axis.isTime():
            bound1 = self.range.values[bound1]
            bound2 = self.range.values[bound2]
        else:
            bound1 = parse_degrees(self.range.values[bound1])
            bound2 = parse_degrees(self.range.values[bound2])
        return self.axis.id, (bound1, bound2)
