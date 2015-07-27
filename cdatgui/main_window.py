from PySide import QtGui, QtCore
from variable_widget import VariableWidget


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent=parent)
        self.setCentralWidget(QtGui.QPlainTextEdit(parent=self))
        self.add_left_dock(VariableWidget(parent=self))

    def add_left_dock(self, widget):
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, widget)

    def add_right_dock(self, widget):
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, widget)

    def add_bottom_dock(self, widget):
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, widget)

    def add_top_dock(self, widget):
        self.addDockWidget(QtCore.Qt.DockWidgetArea.TopDockWidgetArea, widget)
