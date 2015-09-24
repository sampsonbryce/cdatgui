from PySide import QtGui, QtCore


class PrecisionSlider(QtGui.QSlider):
    preciseValueChanged = QtCore.Signal(float)

    def __init__(self, precision=.01, max=100, min=0, value=None, parent=None):
        super(PrecisionSlider, self).__init__(parent=parent)
        self.precision = precision

        self.setMaximum(max)
        self.setMinimum(min)
        self.setValue(value if value is not None else min)
        self.sliderMoved.connect(self.moved)

    def moved(self, value):
        self.preciseValueChanged.emit(value * self.precision)

    def value(self):
        v = super(PrecisionSlider, self).value()
        return v * self.precision

    def setValue(self, v):
        v /= self.precision
        super(PrecisionSlider, self).setValue(v)
        self.preciseValueChanged.emit(v * self.precision)

    def maximum(self):
        v = super(PrecisionSlider, self).maximum()
        return v * self.precision

    def setMaximum(self, v):
        v /= self.precision
        super(PrecisionSlider, self).setMaximum(v)

    def minimum(self):
        v = super(PrecisionSlider, self).minimum()
        return v * self.precision

    def setMinimum(self, v):
        v /= self.precision
        super(PrecisionSlider, self).setMinimum(v)
