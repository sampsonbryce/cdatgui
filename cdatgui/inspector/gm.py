from PySide import QtGui, QtCore
from cdatgui.utils import label
from cdatgui.editors.boxfill import BoxfillEditor


class GraphicsMethodInspector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphicsMethodInspector, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.plot = None
        self.editor = BoxfillEditor()
        layout.addWidget(self.editor)
        self.editor.graphicsMethodUpdated.connect(self.updatePlots)

    def updatePlots(self, gm):
        self.plot.plot()

    def setPlots(self, plots):
        if plots:
            self.plot = plots[0]
            if plots[0].graphics_method:
                self.editor.gm = plots[0].graphics_method
