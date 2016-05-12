from PySide import QtGui, QtCore

from cdatgui.console.console_dock import ConsoleDockWidget
from graphics.graphics_method_widget import GraphicsMethodWidget
from main_menu import MainMenu
from sidebar.inspector_widget import InspectorWidget
from spreadsheet.window import SpreadsheetWindow
from templates.template_widget import TemplateWidget
from variables.variable_widget import VariableWidget

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
        gm_widget.editedGM.connect(self.spreadsheet.tabController.currentWidget().replotPlottersUpdateVars)
        self.add_left_dock(gm_widget)

        tmpl_widget = TemplateWidget(parent=self)
        tmpl_widget.editedTmpl.connect(self.spreadsheet.tabController.currentWidget().replotPlottersUpdateVars)
        self.add_left_dock(tmpl_widget)

        inspector = InspectorWidget(self.spreadsheet, parent=self)
        self.add_right_dock(inspector)

        con = ConsoleDockWidget(self.spreadsheet, parent=self)
        self.add_right_dock(con)
        mm = MainMenu(self.spreadsheet, var_widget, gm_widget, tmpl_widget)
        self.setMenuBar(mm)

        var_widget.variableListNotEmpty.connect(lambda: mm.edit_data_menu.setEnabled(True))
        var_widget.variableListEmpty.connect(lambda: mm.edit_data_menu.setEnabled(False))

    def add_left_dock(self, widget):
        self.addDockWidget(DockWidgetArea.LeftDockWidgetArea, widget)

    def add_right_dock(self, widget):
        self.addDockWidget(DockWidgetArea.RightDockWidgetArea, widget)

    def add_bottom_dock(self, widget):
        self.addDockWidget(DockWidgetArea.BottomDockWidgetArea, widget)

    def add_top_dock(self, widget):
        self.addDockWidget(DockWidgetArea.TopDockWidgetArea, widget)
