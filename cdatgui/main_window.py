from PySide import QtGui, QtCore

from spreadsheet.window import SpreadsheetWindow
from variables import VariableWidget
from graphics import GraphicsMethodWidget
from templates import TemplateWidget
from plotter import PlotManager
import vcs

DockWidgetArea = QtCore.Qt.DockWidgetArea


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent=parent)
        self.setWindowTitle(u"CDATGUI")
        self.spreadsheet = SpreadsheetWindow(f=QtCore.Qt.Widget)

        self.manager = PlotManager(self.spreadsheet.getCell(0, 0))
        self.manager.graphics_method = vcs.getboxfill()
        self.manager.template = vcs.gettemplate('default')

        self.setCentralWidget(self.spreadsheet)

        var_widget = VariableWidget(parent=self)
        var_widget.selectedVariable.connect(self.update_var_on_main)
        self.add_left_dock(var_widget)

        gm_widget = GraphicsMethodWidget(parent=self)
        gm_widget.selectedGraphicsMethod.connect(self.update_gm_on_main)
        self.add_left_dock(gm_widget)

        tmpl_widget = TemplateWidget(parent=self)
        tmpl_widget.selectedTemplate.connect(self.update_tmpl_on_main)
        self.add_left_dock(tmpl_widget)

    def update_var_on_main(self, var):
        self.manager.variables = (var, None)
        try:
            self.manager.plot()
        except ValueError:
            print "Waiting on GM"

    def update_gm_on_main(self, gm):
        self.manager.graphics_method = gm
        try:
            self.manager.plot()
        except ValueError:
            print "Waiting on variables"

    def update_tmpl_on_main(self, tmpl):
        self.manager.template = tmpl
        try:
            self.manager.plot()
        except ValueError:
            print "Waiting on gm/variables"

    def add_left_dock(self, widget):
        self.addDockWidget(DockWidgetArea.LeftDockWidgetArea, widget)

    def add_right_dock(self, widget):
        self.addDockWidget(DockWidgetArea.RightDockWidgetArea, widget)

    def add_bottom_dock(self, widget):
        self.addDockWidget(DockWidgetArea.BottomDockWidgetArea, widget)

    def add_top_dock(self, widget):
        self.addDockWidget(DockWidgetArea.TopDockWidgetArea, widget)
