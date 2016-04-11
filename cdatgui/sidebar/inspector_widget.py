from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from .plot import PlotInspector
from .var import VariableInspector
from .gm import GraphicsMethodInspector
from cdatgui.editors.template import TemplateEditor


class InspectorWidget(StaticDockWidget):
    plotters_updated = QtCore.Signal(list)

    def __init__(self, spreadsheet, parent=None):
        super(InspectorWidget, self).__init__("Inspector", parent=parent)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.RightDockWidgetArea]
        spreadsheet.selectionChanged.connect(self.selection_change)
        self.cells = []

        w = QtGui.QTabWidget()
        pi = PlotInspector()
        self.plotters_updated.connect(pi.setPlots)
        w.addTab(pi, "Plots")

        """
                v = VariableInspector()
                self.plotters_updated.connect(v.setPlots)
                w.addTab(v, "Data")
        """
        gm = GraphicsMethodInspector()
        self.plotters_updated.connect(gm.setPlots)
        w.addTab(gm, "GM")

        tmpl = TemplateEditor()
        self.plotters_updated.connect(tmpl.setPlots)
        w.addTab(tmpl, "Layout")

        self.setWidget(w)

    def update(self):
        for plot in self.plots:
            plot.plot()

    def added_plot(self, displayplot):
        for cell in self.cells:
            if displayplot.name in cell.canvas.display_names:
                cell.loadPlot(displayplot)
                break

    def selection_change(self, selected):
        plots = []
        self.cells = []
        for cell in selected:
            cell = cell.containedWidget
            self.cells.append(cell)
            # cell is now a QCDATWidget
            plots.extend(cell.getPlotters())
        self.plots = plots
        #        print "SELECTION CHANGED CANVAS", self.plots[0].canvas
        self.plotters_updated.emit(self.plots)

