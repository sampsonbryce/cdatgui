from static_docked import StaticDockWidget
from PySide import QtCore


class VariableWidget(StaticDockWidget):

    def __init__(self, parent=None, flags=0):
        super(VariableWidget, self).__init__(u"Variables", parent, flags)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]
