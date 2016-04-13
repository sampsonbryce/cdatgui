from PySide import QtGui, QtCore


class ToolTipSlider(QtGui.QSlider):

    def __init__(self, parent=None):
        super(ToolTipSlider, self).__init__(parent=parent)
        self.sliderPressed.connect(self.show_tooltip)
        self.sliderReleased.connect(self.hide_tooltip)
        self.valueChanged.connect(self.update_tooltip)
        self.setTracking(True)
        self.showing = False

    def show_tooltip(self):
        self.showing = True
        QtGui.QToolTip.showText(QtGui.QCursor.pos(), "%d" % self.value(), self)

    def hide_tooltip(self):
        self.showing = False
        QtGui.QToolTip.hideText()

    def update_tooltip(self, value):
        if self.showing:
            QtGui.QToolTip.showText(QtGui.QCursor.pos(), "%d" % value, self)
