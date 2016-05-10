from PySide import QtGui
from .graphics_method_editor import GraphicsMethodEditorWidget
from .secondary.editor.marker import MarkerEditorWidget
from .secondary.editor.line import LineEditorWidget
import vcs

class VectorEditor(GraphicsMethodEditorWidget):
    """Configures a meshfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(VectorEditor, self).__init__(parent=parent)

        self.button_layout.takeAt(0).widget().deleteLater()
        self.button_layout.takeAt(0).widget().deleteLater()

        line_button = QtGui.QPushButton("Edit Line")
        line_button.clicked.connect(self.editLine)

        self.button_layout.insertWidget(0, line_button)

        self.marker_editor = None
        self.line_editor = None

    def editLine(self):
        if not self.line_editor:
            self.line_editor = LineEditorWidget()
            self.line_editor.accepted.connect(self.updateLine)
        line_obj = vcs.createline(ltype=self.gm.line, color=self.gm.linecolor, width=self.gm.linewidth)
        self.line_editor.setLineObject(line_obj)
        self.line_editor.raise_()
        self.line_editor.show()

    def updateLine(self, name):
        self.gm.line = self.line_editor.object.type[0]
        self.gm.linecolor = self.line_editor.object.color[0]
        self.gm.line = self.line_editor.object.width[0]
