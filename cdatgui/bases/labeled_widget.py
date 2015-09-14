from PySide import QtGui, QtCore


class LabeledWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LabeledWidget, self).__init__(parent=parent)
        self._label = QtGui.QLabel()
        self.w = None
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._label)
        self.setLayout(layout)

    def get_widget(self):
        return self.w

    def set_widget(self, w):
        if self.w is not None:
            self.layout().removeWidget(self.w)
            self.w.deleteLater()
        self.layout().addWidget(w)
        self.w = w

    widget = property(get_widget, set_widget)

    def get_label(self):
        return self._label.text()

    def set_label(self, t):
        self._label.setText(t)

    label = property(get_label, set_label)