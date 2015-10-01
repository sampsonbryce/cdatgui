from PySide import QtGui, QtCore
from cdatgui.utils import label


class ConsoleInspector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ConsoleInspector, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(label("Coming Soon"))
