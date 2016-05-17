from PySide import QtGui, QtCore
from value_slider import ValueSlider


class RangeValidator(QtGui.QValidator):
    validInput = QtCore.Signal()
    invalidInput = QtCore.Signal()

    def __init__(self, min, max, parse, parent=None):
        super(RangeValidator, self).__init__(parent=parent)
        self.min = min
        self.max = max
        self.parser = parse

    def validate(self, i, pos):
        value = self.parser(i)
        if value is not None and value <= self.max and value >= self.min:
            self.validInput.emit()
            return self.Acceptable
        else:
            self.invalidInput.emit()
            return self.Intermediate


def __build_slider__(val, values):
    s = ValueSlider(values)
    if val in values:
        s.setRealValue(val)
    else:
        s.setValue(val)
    s.setTracking(True)
    s.setOrientation(QtCore.Qt.Horizontal)
    s.sizePolicy().setHorizontalPolicy(QtGui.QSizePolicy.MinimumExpanding)
    s.sizePolicy().setHorizontalStretch(10)
    return s


class RangeWidget(QtGui.QWidget):
    boundsEdited = QtCore.Signal()
    validParams = QtCore.Signal()
    invalidParams = QtCore.Signal()

    def __init__(self, values, bottom=None, top=None, circular=False, parent=None):
        """
        min: Minimum value for range
        max: Maximum value for range
        bottom: Lower bound
        top: Upper bound
        formatter: Callable that converts a value to a string
        parser: Callable that converts a string to a value
        """
        super(RangeWidget, self).__init__(parent=parent)
        self.flipped = False
        self.values = values
        l = QtGui.QHBoxLayout()

        if bottom is None:
            bottom = 0

        if top is None:
            top = len(values) - 1
        min = 0
        max = len(values) - 1

        self.lowerBoundText = QtGui.QLineEdit(self.format(bottom))
        self.upperBoundText = QtGui.QLineEdit(self.format(top))

        lower_validator = RangeValidator(min, top, self.parse)
        upper_validator = RangeValidator(bottom, max, self.parse)

        lower_validator.validInput.connect(self.validParams.emit)
        lower_validator.invalidInput.connect(self.invalidParams.emit)
        upper_validator.validInput.connect(self.validParams.emit)
        upper_validator.invalidInput.connect(self.invalidParams.emit)

        self.lowerBoundText.setValidator(lower_validator)
        self.upperBoundText.setValidator(upper_validator)

        self.lowerBoundSlider = __build_slider__(bottom, values)
        self.upperBoundSlider = __build_slider__(top, values)

        slayout = QtGui.QVBoxLayout()
        slayout.addWidget(self.lowerBoundSlider, 1)
        slayout.addWidget(self.upperBoundSlider, 1)

        l.addWidget(self.lowerBoundText)
        l.addLayout(slayout, 1)
        l.addWidget(self.upperBoundText)

        self.lowerBoundSlider.valueChanged.connect(self.updateLower)
        self.upperBoundSlider.valueChanged.connect(self.updateUpper)

        self.lowerBoundText.textEdited.connect(self.parseLower)
        self.upperBoundText.textEdited.connect(self.parseUpper)

        self.lowerBoundText.editingFinished.connect(self.adjustLower)
        self.upperBoundText.editingFinished.connect(self.adjustUpper)

        self.errorPalette = QtGui.QPalette()
        self.errorPalette.setColor(self.errorPalette.Text, QtCore.Qt.red)
        self.validPalette = QtGui.QPalette()
        self.validPalette.setColor(self.validPalette.Text, QtCore.Qt.black)

        self.setLayout(l)

    def getLimits(self):
        return self.lowerBoundSlider.minimum(), self.lowerBoundSlider.maximum()

    def format(self, ind):
        return self.values[ind]

    def parse(self, value):
        for i, v in enumerate(self.values):
            if v.startswith(value):
                return i

    def getBounds(self):
        return self.lowerBoundSlider.value(), self.upperBoundSlider.value()

    def setBounds(self, low, high):
        self.lowerBoundSlider.setValue(low)
        self.upperBoundSlider.setValue(high)

    def updateLower(self, value):
        if value > self.upperBoundSlider.value() and not self.flipped:
            self.values.reverse()
            self.flipped = True
        elif value < self.upperBoundSlider.value() and self.flipped:
            self.values.reverse()
            self.flipped = False

        self.upperBoundText.setText(self.format(self.upperBoundSlider.value()))
        self.boundsEdited.emit()
        if value != self.parse(self.lowerBoundText.text()):
            self.lowerBoundText.setText(self.format(value))

    def updateUpper(self, value):
        if value < self.lowerBoundSlider.value() and not self.flipped:
            self.values.reverse()
            self.flipped = True
        elif value > self.lowerBoundSlider.value() and self.flipped:
            self.values.reverse()
            self.flipped = False

        self.lowerBoundText.setText(self.format(self.lowerBoundSlider.value()))
        self.boundsEdited.emit()
        if value != self.parse(self.upperBoundText.text()):
            self.upperBoundText.setText(self.format(value))

    def parseLower(self, t):
        if self.lowerBoundText.hasAcceptableInput():
            val = self.parse(t)
            self.lowerBoundSlider.setValue(val)
            self.lowerBoundText.setPalette(self.validPalette)
        else:
            self.lowerBoundText.setPalette(self.errorPalette)

    def parseUpper(self, t):
        if self.upperBoundText.hasAcceptableInput():
            val = self.parse(t)
            self.upperBoundSlider.setValue(val)
            self.upperBoundText.setPalette(self.validPalette)
        else:
            self.upperBoundText.setPalette(self.errorPalette)

    def adjustLower(self):
        if self.lowerBoundText.hasAcceptableInput():
            # Normalize the value
            value = self.parse(self.lowerBoundText.text())
            self.lowerBoundText.setText(self.format(value))

    def adjustUpper(self):
        if self.upperBoundText.hasAcceptableInput():
            # Normalize the value
            value = self.parse(self.upperBoundText.text())
            self.upperBoundText.setText(self.format(value))
