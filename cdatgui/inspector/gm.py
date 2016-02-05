from PySide import QtGui, QtCore
from cdatgui.utils import label
from cdatgui.editors.level_editor import LevelEditor


class GraphicsMethodInspector(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphicsMethodInspector, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.editor = LevelEditor()
        layout.addWidget(self.editor)

    def setPlots(self, plots):
        if plots:
            self.editor.gm = plots[0].graphics_method
            self.editor.var = plots[0].variables[0]
