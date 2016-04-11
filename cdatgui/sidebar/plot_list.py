from PySide import QtGui, QtCore
from cdatgui.utils import label, header_label, icon


class PlotItem(QtGui.QWidget):

    # Passes self to a parent so this object can be removed
    removeAction = QtCore.Signal(object)

    def __init__(self, plotter, parent=None):
        super(PlotItem, self).__init__(parent=parent)
        self.plotter = plotter
        l = QtGui.QHBoxLayout()
        self.setLayout(l)
        b = QtGui.QPushButton()
        b.setIcon(icon("editdelete.png"))
        b.setIconSize(QtCore.QSize(16, 16))
        b.setFlat(True)
        b.resize(QtCore.QSize(16, 16))
        l.addWidget(b)
        b.clicked.connect(self.remove)
        l.addWidget(label(self.plotter.name()))

    def remove(self, checked=False):
        self.removeAction.emit(self)
        self.plotter.remove()


class PlotList(QtGui.QWidget):

    def __init__(self, parent=None):
        super(PlotList, self).__init__(parent=parent)
        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        l.addWidget(header_label("Plots"))
        self._plots = []

    def clear(self):
        for p in self._plots:
            self.removeItem(p)

    def removeItem(self, pi):
        self.layout().removeWidget(pi)
        self._plots.remove(pi)
        pi.deleteLater()

    def plots(self):
        return self._plots

    def set_plots(self, plots):
        self.clear()
        for p in plots:
            pi = PlotItem(p)
            self.addItem(pi)

    plots = property(plots, set_plots)

    def addItem(self, pi):
        self._plots.append(pi)
        self.layout().addWidget(pi)
        pi.removeAction.connect(self.removeItem)
