import vtk
import os
import platform
from PySide import QtCore, QtGui
import vcs
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VTKWidget(QtGui.QFrame):
    becameDrawable = QtCore.Signal()

    def __init__(self, parent=None, f=0):
        super(VTKWidget, self).__init__(parent=parent, f=f)

        self.ren_win = vtk.vtkRenderWindow()
        self.inter = QVTKRenderWindowInteractor(parent=self, rw=self.ren_win)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.inter)
        self.setLayout(layout)

        self.events = (self.ren_win.AddObserver("ModifiedEvent",
                                                self.modified),
                       self.inter.AddObserver("ConfigureEvent",
                                              self.modified)
                       )

    def isDrawable(self):
        # Need to redirect stderr to quash the Invalid Drawable errors?
        val = self.ren_win.IsDrawable()
        return val

    def modified(self, obj, ev):
        if self.ren_win.IsDrawable():
            self.ren_win.RemoveObserver(self.events[0])
            self.inter.RemoveObserver(self.events[1])
            self.becameDrawable.emit()


class QCDATWidget(QtGui.QWidget):
    canvasReady = QtCore.Signal()

    save_formats = ["PNG file (*.png)",
                    "GIF file (*.gif)",
                    "PDF file (*.pdf)",
                    "Postscript file (*.ps)",
                    "SVG file (*.svg)"]

    def __init__(self, parent=None, f=0):
        super(QCDATWidget, self).__init__(parent=parent, f=f)

        self.vtk = VTKWidget(parent=self, f=f)

        self.canvas = None

        def init_canvas():
            self.canvas = vcs.init(backend=self.vtk.ren_win)
            self.canvas.open()
            self.canvasReady.emit()

        if self.vtk.isDrawable() is False:
            # There's a weird Qt/VTK bug that spews out "Invalid Drawable"
            # until the window is fully initialized and visible. We'll wait
            # until mRenWin.IsDrawable is True, then init the canvas
            self.vtk.becameDrawable.connect(init_canvas)
        else:
            init_canvas()

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.vtk)
        self.setLayout(self.layout)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))
        self.h_timer = None
        self.s_timer = None
        # Just need a callable that returns something
        self.toolBarType = lambda x: None

    def prepExtraDims(self, var):
        k = {}
        for d, i in zip(self.extraDimsNames, self.extraDimsIndex):
            if d in var.getAxisIds():
                k[d] = slice(i, None)
        return k

    def get_graphics_method(self, plotType, gmName):
        method_name = "get" + str(plotType).lower()
        return getattr(self.canvas, method_name)(gmName)

    def deleteLater(self):
        """ deleteLater() -> None
        Make sure to free render window resource when
        deallocating. Overriding PyQt deleteLater to free up
        resources
        """

        if self.canvas is not None:
            self.canvas.onClosing((0, 0))
            self.canvas = None
        if self.s_timer is not None:
            self.s_timer.stop()
            self.s_timer = None
        if self.h_timer is not None:
            self.h_timer.stop()
            self.h_timer = None

        QtGui.QWidget.deleteLater(self)

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
