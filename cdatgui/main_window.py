from PySide import QtGui, QtCore

from spreadsheet.window import SpreadsheetWindow
from variables.variable_widget import VariableWidget
from graphics.graphics_method_widget import GraphicsMethodWidget
from templates.template_widget import TemplateWidget
from inspector.inspector_widget import InspectorWidget
from main_menu import MainMenu
import vcs

DockWidgetArea = QtCore.Qt.DockWidgetArea


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent=parent)
        self.setWindowTitle(u"CDATGUI")
        self.spreadsheet = SpreadsheetWindow(f=QtCore.Qt.Widget)

        self.setCentralWidget(self.spreadsheet)

        var_widget = VariableWidget(parent=self)
        self.add_left_dock(var_widget)

        gm_widget = GraphicsMethodWidget(parent=self)
        self.add_left_dock(gm_widget)

        tmpl_widget = TemplateWidget(parent=self)
        self.add_left_dock(tmpl_widget)

        inspector = InspectorWidget(self.spreadsheet, parent=self)
        self.add_right_dock(inspector)

        self.setMenuBar(MainMenu(self.spreadsheet, var_widget,
                                 gm_widget, tmpl_widget))

    def add_left_dock(self, widget):
        self.addDockWidget(DockWidgetArea.LeftDockWidgetArea, widget)

    def add_right_dock(self, widget):
        self.addDockWidget(DockWidgetArea.RightDockWidgetArea, widget)

    def add_bottom_dock(self, widget):
        self.addDockWidget(DockWidgetArea.BottomDockWidgetArea, widget)

    def add_top_dock(self, widget):
        self.addDockWidget(DockWidgetArea.TopDockWidgetArea, widget)
