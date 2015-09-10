from PySide import QtGui


class PlotList(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(PlotList, self).__init__(parent=parent)
        self._plots = []

    def plots(self):
        return self._plots

    def set_plots(self, plots):
        self.clear()

        self._plots = plots

        for plot in self._plots:
            self.addItem(plot.name())

    plots = property(plots, set_plots)
