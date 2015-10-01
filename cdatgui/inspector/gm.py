from PySide import QtGui, QtCore
from cdatgui.utils import label


class GraphicsMethodInspector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphicsMethodInspector, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(label("Coming Soon"))
