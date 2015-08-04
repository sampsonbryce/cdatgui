from PySide import QtGui, QtCore
from variables import VariableWidget
from spreadsheet.window import SpreadsheetWindow


DockWidgetArea = QtCore.Qt.DockWidgetArea


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent=parent)
        self.spreadsheet = SpreadsheetWindow(f=QtCore.Qt.Widget)
        self.setCentralWidget(self.spreadsheet)
        var_widget = VariableWidget(parent=self)
        var_widget.selectedVariable.connect(self.update_var_on_main)
        self.add_left_dock(var_widget)

    def update_var_on_main(self, var):
        canvas = self.spreadsheet.getCanvas(0, 0)
        canvas.clear()
        canvas.plot(var)

    def add_left_dock(self, widget):
        self.addDockWidget(DockWidgetArea.LeftDockWidgetArea, widget)

    def add_right_dock(self, widget):
        self.addDockWidget(DockWidgetArea.RightDockWidgetArea, widget)

    def add_bottom_dock(self, widget):
        self.addDockWidget(DockWidgetArea.BottomDockWidgetArea, widget)

    def add_top_dock(self, widget):
        self.addDockWidget(DockWidgetArea.TopDockWidgetArea, widget)
