from PySide import QtGui, QtCore

from cdatgui.utils import label
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

    def __init__(self, values, bottom=None, top=None, axis_type=None, flipped=False, parent=None):
        """
        values: Axis values to be used for slider
        bottom: Lower bound
        top: Upper bound
        axis_type: Axis type to set up slider labels
        flipped: the graph was flipped previously or not
        """
        super(RangeWidget, self).__init__(parent=parent)
        self.flipped = flipped
        self.values = values
        self.center = False

        if bottom is None:
            bottom = 0

        if top is None:
            top = len(values) - 1
        self.min = 0
        self.max = len(values) - 1
        self.prev_diff = top - bottom

        self.lowerBoundText = QtGui.QLineEdit(self.format(bottom))
        self.lowerBoundText.setFixedWidth(120)
        self.upperBoundText = QtGui.QLineEdit(self.format(top))
        self.upperBoundText.setFixedWidth(120)

        lower_validator = RangeValidator(self.min, self.max, self.parse)
        upper_validator = RangeValidator(self.min, self.max, self.parse)

        lower_validator.validInput.connect(self.validParams.emit)
        lower_validator.invalidInput.connect(self.invalidParams.emit)
        upper_validator.validInput.connect(self.validParams.emit)
        upper_validator.invalidInput.connect(self.invalidParams.emit)

        self.lowerBoundText.setValidator(lower_validator)
        self.upperBoundText.setValidator(upper_validator)

        self.lowerBoundSlider = __build_slider__(bottom, values)
        self.upperBoundSlider = __build_slider__(top, values)

        self.lowerBoundSlider.valueChanged.connect(self.updateLower)
        self.upperBoundSlider.valueChanged.connect(self.updateUpper)

        self.lowerBoundText.textEdited.connect(self.parseLower)
        self.upperBoundText.textEdited.connect(self.parseUpper)

        self.lowerBoundText.editingFinished.connect(self.adjustLower)
        self.upperBoundText.editingFinished.connect(self.adjustUpper)

        self.upperTimer = QtCore.QTimer()
        self.upperTimer.setInterval(1000)
        self.upperTimer.timeout.connect(self.adjustUpper)

        self.lowerTimer = QtCore.QTimer()
        self.lowerTimer.setInterval(1000)
        self.lowerTimer.timeout.connect(self.adjustLower)

        self.errorPalette = QtGui.QPalette()
        self.errorPalette.setColor(self.errorPalette.Text, QtCore.Qt.red)
        self.validPalette = QtGui.QPalette()
        self.validPalette.setColor(self.validPalette.Text, QtCore.Qt.black)

        full_layout = QtGui.QHBoxLayout()
        label_layout = QtGui.QVBoxLayout()
        if axis_type == 'latitude':
            label_layout.addWidget(label('Bottom:'))
            label_layout.addWidget(label('Top:'))
        elif axis_type == 'longitude':
            label_layout.addWidget(label('Left:'))
            label_layout.addWidget(label('Right:'))
        elif axis_type == 'time':
            label_layout.addWidget(label('Start:'))
            label_layout.addWidget(label('End:'))

        lower_layout = QtGui.QHBoxLayout()
        lower_layout.addWidget(self.lowerBoundText)
        lower_layout.addWidget(self.lowerBoundSlider)

        upper_layout = QtGui.QHBoxLayout()
        upper_layout.addWidget(self.upperBoundText)
        upper_layout.addWidget(self.upperBoundSlider)

        slayout = QtGui.QVBoxLayout()
        slayout.addLayout(lower_layout, 1)
        slayout.addLayout(upper_layout, 1)

        full_layout.addLayout(label_layout)
        full_layout.addLayout(slayout)

        if axis_type == 'latitude' or axis_type == 'longitude':
            self.center = True
            self.centerLineSlider = __build_slider__((bottom + top) / 2, values)
            self.centerLineText = QtGui.QLineEdit()
            self.centerLineText.setFixedWidth(120)
            center_validator = RangeValidator(self.min, self.max, self.parse)
            center_validator.validInput.connect(self.validParams.emit)
            center_validator.invalidInput.connect(self.invalidParams.emit)
            self.centerTimer = QtCore.QTimer()
            self.centerTimer.setInterval(1000)
            self.centerTimer.timeout.connect(self.adjustCenter)
            self.centerLineText.setValidator(center_validator)
            self.centerLineSlider.valueChanged.connect(self.updateCenter)
            self.centerLineText.textEdited.connect(self.parseCenter)
            self.centerLineText.editingFinished.connect(self.adjustCenter)
            center_layout = QtGui.QHBoxLayout()
            label_layout.insertWidget(1, label('Position:'))
            center_layout.addWidget(self.centerLineText)
            center_layout.addWidget(self.centerLineSlider)
            slayout.insertLayout(1, center_layout)
            self.recenterCenter()

        self.setLayout(full_layout)

    def getLimits(self):
        return self.lowerBoundSlider.minimum(), self.lowerBoundSlider.maximum()

    def format(self, ind):
        return self.values[ind]

    def parse(self, value):
        for i, v in enumerate(self.values):
            if v.startswith(value):
                return i
        return None

    def getBounds(self):
        return self.lowerBoundSlider.value(), self.upperBoundSlider.value()

    def setBounds(self, low, high):
        self.lowerBoundSlider.setValue(low)
        self.upperBoundSlider.setValue(high)

    def updateLower(self, value):
        if value > self.upperBoundSlider.value() and not self.flipped:
            self.flipped = True
        elif value < self.upperBoundSlider.value() and self.flipped:
            self.flipped = False

        self.upperBoundText.setText(self.format(self.upperBoundSlider.value()))
        self.recenterCenter()
        self.boundsEdited.emit()
        self.lowerBoundText.setPalette(self.validPalette)
        if value != self.parse(self.lowerBoundText.text()):
            self.lowerBoundText.setText(self.format(value))

        # update diff
        self.prev_diff = self.upperBoundSlider.value() - self.lowerBoundSlider.value()

    def updateCenter(self, value=None):
        recenter = False

        if self.prev_diff % 2 == 1:
            diff = self.prev_diff - 1
        else:
            diff = self.prev_diff
        diff /= 2

        if value - diff < self.min:
            lower_val = self.min
            self.centerLineText.validator().min = value
            upper_val = lower_val + self.prev_diff
            recenter = True
        elif value + diff > self.max:
            upper_val = self.max
            self.centerLineText.validator().max = value
            lower_val = upper_val - self.prev_diff
            recenter = True
        else:
            lower_val = self.centerLineSlider.value() - diff
            upper_val = self.centerLineSlider.value() + diff

        block = self.lowerBoundSlider.blockSignals(True)
        self.lowerBoundSlider.setValue(lower_val)

        self.lowerBoundSlider.blockSignals(block)
        self.lowerBoundText.setText(self.format(self.lowerBoundSlider.value()))

        self.centerLineText.setPalette(self.validPalette)

        block = self.upperBoundSlider.blockSignals(True)
        self.upperBoundSlider.setValue(upper_val)
        self.upperBoundText.setText(self.format(self.upperBoundSlider.value()))
        self.upperBoundSlider.blockSignals(block)

        block = self.centerLineText.blockSignals(True)
        self.centerLineText.setText(self.format(self.centerLineSlider.value()))
        self.centerLineText.blockSignals(block)

        if recenter:
            self.recenterCenter()

        self.boundsEdited.emit()

    def recenterCenter(self):
        if not self.center:
            return

        diff = abs(self.upperBoundSlider.value() - self.lowerBoundSlider.value())
        if diff % 2 == 1:
            diff -= 1
        diff /= 2

        block = self.centerLineSlider.blockSignals(True)
        if not self.flipped:
            self.centerLineSlider.setValue(self.lowerBoundSlider.value() + diff)
        else:
            self.centerLineSlider.setValue(self.lowerBoundSlider.value() - diff)
        self.centerLineSlider.blockSignals(block)

        self.centerLineText.setText(self.format(self.centerLineSlider.value()))
        self.centerLineText.setPalette(self.validPalette)
        return diff

    def updateUpper(self, value):
        if value < self.lowerBoundSlider.value() and not self.flipped:
            self.flipped = True
        elif value > self.lowerBoundSlider.value() and self.flipped:
            self.flipped = False

        self.lowerBoundText.setText(self.format(self.lowerBoundSlider.value()))
        self.recenterCenter()
        self.boundsEdited.emit()
        self.upperBoundText.setPalette(self.validPalette)
        if value != self.parse(self.upperBoundText.text()):
            self.upperBoundText.setText(self.format(value))

        # update diff
        self.prev_diff = self.upperBoundSlider.value() - self.lowerBoundSlider.value()

    def parseLower(self, t):
        self.lowerTimer.start()
        if self.lowerBoundText.hasAcceptableInput():
            val = self.parse(t)
            block = self.lowerBoundSlider.blockSignals(True)
            self.lowerBoundSlider.setValue(val)
            self.lowerBoundSlider.blockSignals(block)
            self.lowerBoundText.setPalette(self.validPalette)
        else:
            self.lowerBoundText.setPalette(self.errorPalette)

    def parseCenter(self, t):
        self.centerTimer.start()
        if self.centerLineText.hasAcceptableInput():
            val = self.parse(t)
            block = self.centerLineSlider.blockSignals(True)
            self.centerLineSlider.setValue(val)
            self.centerLineSlider.blockSignals(block)
            self.centerLineText.setPalette(self.validPalette)
        else:
            self.centerLineText.setPalette(self.errorPalette)

    def parseUpper(self, t):
        self.upperTimer.start()
        if self.upperBoundText.hasAcceptableInput():
            val = self.parse(t)
            block = self.upperBoundSlider.blockSignals(True)
            self.upperBoundSlider.setValue(val)
            self.upperBoundSlider.blockSignals(block)
            self.upperBoundText.setPalette(self.validPalette)
        else:
            self.upperBoundText.setPalette(self.errorPalette)

    def adjustLower(self):
        if self.lowerBoundText.hasAcceptableInput():
            # Normalize the value
            value = self.parse(self.lowerBoundText.text())
            self.lowerBoundText.setText(self.format(value))
            self.updateLower(value)

    def adjustCenter(self):
        if self.centerLineText.hasAcceptableInput():
            # Normalize the value
            value = self.parse(self.centerLineText.text())
            self.centerLineText.setText(self.format(value))
            self.updateCenter(value)

    def adjustUpper(self):
        if self.upperBoundText.hasAcceptableInput():
            # Normalize the value
            value = self.parse(self.upperBoundText.text())
            self.upperBoundText.setText(self.format(value))
            self.updateUpper(value)
