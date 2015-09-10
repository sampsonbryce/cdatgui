from PySide import QtCore
from cdatgui.bases import StaticDockWidget
from plot_list import PlotList


class InspectorWidget(StaticDockWidget):

    def __init__(self, spreadsheet, parent=None):
        super(InspectorWidget, self).__init__("Inspector", parent=parent)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.RightDockWidgetArea]
        self.plot_list = PlotList(parent=self)
        self.setWidget(self.plot_list)
        spreadsheet.selectionChanged.connect(self.selection_change)

    def selection_change(self, selected):
        plots = []
        for cell in selected:
            cell = cell.containedWidget
            # cell is now a QCDATWidget
            plots.extend(cell.getPlotters())

        self.plot_list.plots = plots
