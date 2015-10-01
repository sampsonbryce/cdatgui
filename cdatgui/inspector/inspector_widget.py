from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from .plot import PlotInspector
from .var import VariableInspector
from .gm import GraphicsMethodInspector
from .templ import TemplateInspector
from .console import ConsoleInspector


class InspectorWidget(StaticDockWidget):
    plotters_updated = QtCore.Signal(list)

    def __init__(self, spreadsheet, parent=None):
        super(InspectorWidget, self).__init__("Inspector", parent=parent)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.RightDockWidgetArea]
        spreadsheet.selectionChanged.connect(self.selection_change)

        w = QtGui.QTabWidget()
        pi = PlotInspector()
        self.plotters_updated.connect(pi.setPlots)
        w.addTab(pi, "Plots")

        v = VariableInspector()
        self.plotters_updated.connect(v.setPlots)
        w.addTab(v, "Data")

        gm = GraphicsMethodInspector()
        w.addTab(gm, "Viz")

        tmpl = TemplateInspector()
        w.addTab(tmpl, "Layout")

        con = ConsoleInspector()
        w.addTab(con, "Python")

        self.setWidget(w)

    def selection_change(self, selected):
        plots = []
        for cell in selected:
            cell = cell.containedWidget
            # cell is now a QCDATWidget
            plots.extend(cell.getPlotters())

        self.plots = plots
        self.plotters_updated.emit(self.plots)
