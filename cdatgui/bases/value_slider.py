from PySide import QtGui, QtCore


class ValueSlider(QtGui.QSlider):
    realValueChanged = QtCore.Signal(object)

    def __init__(self, values, parent=None):
        super(ValueSlider, self).__init__(parent=parent)
        self.values = values
        self.setMinimum(0)
        self.setMaximum(len(values) - 1)
        self.valueChanged.connect(self.emitReal)

    def emitReal(self, val):
        self.realValueChanged.emit(self.values[val])

    def realValue(self):
        return self.values[self.value()]

    def setRealValue(self, realValue):
        if isinstance(realValue, list):
            realValue = realValue[0]
        val = min(range(len(self.values)), key=lambda i: abs(self.values[i]-realValue))
        self.setValue(val)
