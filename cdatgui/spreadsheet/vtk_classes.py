import vtk
import os
from PySide import QtCore, QtGui
import vcs
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from cdatgui.cdat.plotter import PlotInfo
from functools import partial
from cdatgui.variables import get_variables

cdms_mime = "application/x-cdms-variable-list"
vcs_gm_mime = "application/x-vcs-gm"
vcs_template_mime = "application/x-vcs-template"


class QCDATWidget(QtGui.QFrame):
    # TODO: Add a signal for addedPlots
    plotAdded = QtCore.Signal()
    visiblityChanged = QtCore.Signal(bool)
    setVariables = QtCore.Signal(list)
    setGraphicsMethod = QtCore.Signal(object)
    setTemplate = QtCore.Signal(object)
    emitAllPlots = QtCore.Signal()

    save_formats = ["PNG file (*.png)",
                    "GIF file (*.gif)",
                    "PDF file (*.pdf)",
                    "Postscript file (*.ps)",
                    "SVG file (*.svg)"]

    def __init__(self, row, col, parent=None):
        super(QCDATWidget, self).__init__(parent=parent)

        self.row = row
        self.col = col

        self.setAcceptDrops(True)

        self.mRenWin = vtk.vtkRenderWindow()
        self.mRenWin.StencilCapableOn()
        self.iren = QVTKRenderWindowInteractor(parent=self, rw=self.mRenWin)
        self.canvas = None

        self.canvasLayout = QtGui.QVBoxLayout()
        self.canvasLayout.addWidget(self.iren)
        self.setLayout(self.canvasLayout)

        self.becameVisible = partial(self.visiblityChanged.emit, True)
        self.becameHidden = partial(self.visiblityChanged.emit, False)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))

        self.visiblityChanged.connect(self.manageCanvas)

        self.dragTarget = QtGui.QWidget(self)
        self.dragTarget.hide()

        self.dragLayout = QtGui.QHBoxLayout()
        self.dragTarget.setLayout(self.dragLayout)
        get_variables().dataChanged.connect(self.variablesChanged)
        self.plots = []
        # Creates and hooks up the initial PlotInfo widget
        self.addedPlot()

        # Just need a callable that returns something
        self.toolBarType = lambda x: None

    def plot_at_point(self, point):
        for plot in self.plots:
            r = plot.frameGeometry()
            if r.contains(point):
                return plot
        return None

    def load(self, displays):
        for display in displays:
            info = self.plots[-1]
            info.load(display)

    def dragMoveEvent(self, event):
        plot = self.plot_at_point(event.pos())
        if plot:
            event.accept(plot.rect())
        else:
            event.ignore()

    def variablesChanged(self, start, end):
        vars = get_variables()
        any_updated = False
        for i in range(start.row(), end.row() + 1):
            var = vars.get(i)
            for plot in self.plots:
                plot_vars = plot.manager.variables
                if plot_vars is None:
                    continue
                changed = False
                new_vars = []
                for v in plot_vars:
                    if v is None:
                        continue
                    if v.id == var.id:
                        changed = True
                        new_vars.append(var.var)
                    else:
                        new_vars.append(v)
                if changed:
                    any_updated = True
                    plot.variables(new_vars)
        if any_updated:
            self.update()

    def dropEvent(self, event):
        dropped = event.source().model().get_dropped(event.mimeData())
        target = self.plot_at_point(event.pos())

        if cdms_mime in event.mimeData().formats():
            event.accept()
            target.variables(dropped)
        if vcs_template_mime in event.mimeData().formats():
            event.accept()
            target.template(dropped)
        if vcs_gm_mime in event.mimeData().formats():
            event.accept()
            target.graphics_method(dropped)

        self.iren.show()
        self.dragTarget.hide()
        self.plotAdded.emit()
        self.emitAllPlots.emit()

    def dragEnterEvent(self, event):
        accepted = set([cdms_mime, vcs_gm_mime, vcs_template_mime])
        if set(event.mimeData().formats()) & accepted:
            event.accept()
        self.dragTarget.resize(self.size())
        self.dragTarget.show()
        self.iren.hide()

    def dragLeaveEvent(self, event=None):
        self.iren.show()
        self.dragTarget.hide()

    def loadPlot(self, dp):
        self.plots[-1].load(dp)

    def addedPlot(self):
        """Adds a new PlotInfo to the collection whenever one is made"""
        new_widget = PlotInfo(lambda: self.canvas, self.row, self.col)
        self.dragLayout.addWidget(new_widget)
        self.plots.append(new_widget)
        new_widget.initialized.connect(self.addedPlot)
        new_widget.removed.connect(self.removeWidget)

    def removeWidget(self, widget):
        self.plots.remove(widget)
        self.dragLayout.removeWidget(widget)
        widget.deleteLater()

    def manageCanvas(self, showing):
        if showing and self.canvas is None:
            self.canvas = vcs.init(backend=self.mRenWin)
            self.canvas.open()
        if not showing and self.canvas is not None:
            self.canvas.onClosing((0, 0))
            self.canvas = None

        self.emitAllPlots.emit()

    def showEvent(self, e):
        super(QCDATWidget, self).showEvent(e)
        QtCore.QTimer.singleShot(0, self.becameVisible)

    def hideEvent(self, e):
        super(QCDATWidget, self).hideEvent(e)
        QtCore.QTimer.singleShot(0, self.becameHidden)

    def prepExtraDims(self, var):
        k = {}
        for d, i in zip(self.extraDimsNames, self.extraDimsIndex):
            if d in var.getAxisIds():
                k[d] = slice(i, None)
        return k

    def get_graphics_method(self, plotType, gmName):
        method_name = "get" + str(plotType).lower()
        return getattr(self.canvas, method_name)(gmName)

    def getPlotters(self):
        return [plot.manager for plot in self.plots]

    def deleteLater(self):
        """ deleteLater() -> None
        Make sure to free render window resource when
        deallocating. Overriding PyQt deleteLater to free up
        resources
        """

        self.canvas.onClosing((0, 0))
        self.canvas = None
        self.dragTarget.deleteLater()
        super(QCDATWidget, self).deleteLater()

    def dumpToFile(self, filename):
        """ dumpToFile(filename: str, dump_as_pdf: bool) -> None
        Dumps itself as an image to a file, calling grabWindowPixmap """
        (_, ext) = os.path.splitext(filename)
        if ext.upper() == '.PDF':
            self.canvas.pdf(filename)
        elif ext.upper() == ".PNG":
            self.canvas.png(filename)
        elif ext.upper() == ".SVG":
            self.canvas.svg(filename)
        elif ext.upper() == ".GIF":
            self.canvas.gif(filename)
        elif ext.upper() == ".PS":
            self.canvas.postscript(filename)

    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> bool
        Save the current widget contents to an image file

        """
        return self.canvas.png(filename)

    def saveToPDF(self, filename):
        """ saveToPDF(filename: str) -> bool
        Save the current widget contents to a pdf file

        """
        self.canvas.pdf(filename)
