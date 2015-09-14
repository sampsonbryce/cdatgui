from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from plot_list import PlotList
from animation import AnimationControls


class InspectorWidget(StaticDockWidget):

    def __init__(self, spreadsheet, parent=None):
        super(InspectorWidget, self).__init__("Inspector", parent=parent)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.RightDockWidgetArea]

        w = QtGui.QWidget()
        l = QtGui.QVBoxLayout()
        w.setLayout(l)

        self.plot_list = PlotList(parent=self)
        l.addWidget(self.plot_list)

        self.animation = AnimationControls()
        l.addWidget(self.animation)

        self.setWidget(w)
        spreadsheet.selectionChanged.connect(self.selection_change)

    def selection_change(self, selected):
        plots = []
        for cell in selected:
            cell = cell.containedWidget
            # cell is now a QCDATWidget
            plots.extend(cell.getPlotters())

        self.plot_list.plots = plots
