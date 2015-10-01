from PySide import QtGui, QtCore
from cdatgui.utils import label


class TemplateInspector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TemplateInspector, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(label("Coming Soon"))
