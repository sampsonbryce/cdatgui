from PySide import QtGui, QtCore
from .graphics_method_editor import GraphicsMethodEditorWidget
from .secondary.editor.marker import MarkerEditorWidget
from .secondary.editor.line import LineEditorWidget
import vcs

class Cdat1dEditor(GraphicsMethodEditorWidget):
    """Configures a meshfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(Cdat1dEditor, self).__init__(parent=parent)

        self.button_layout.takeAt(0).widget().deleteLater()
        self.button_layout.takeAt(0).widget().deleteLater()

        self.flip_check = QtGui.QCheckBox()
        self.flip_check.stateChanged.connect(self.flipGraph)

        flip_layout = QtGui.QHBoxLayout()
        flip_layout.addWidget(QtGui.QLabel("Flip"))
        flip_layout.addWidget(self.flip_check)
        flip_layout.addStretch(1)

        marker_button = QtGui.QPushButton("Edit Marker")
        marker_button.clicked.connect(self.editMarker)

        line_button = QtGui.QPushButton("Edit Line")
        line_button.clicked.connect(self.editLine)

        self.button_layout.insertWidget(0, line_button)
        self.button_layout.insertWidget(0, marker_button)
        self.button_layout.insertLayout(0, flip_layout)

        self.marker_editor = None
        self.line_editor = None

    def editMarker(self):
        if self.marker_editor:
            self.marker_editor.close()
            self.marker_editor.deleteLater()
        self.marker_editor = MarkerEditorWidget()
        self.marker_editor.accepted.connect(self.updateMarker)
        mark_obj = vcs.createmarker(mtype=self.gm.marker, color=self.gm.markercolor, size=self.gm.markersize)
        self.marker_editor.setMarkerObject(mark_obj)
        self.marker_editor.raise_()
        self.marker_editor.show()

    def editLine(self):
        if self.line_editor:
            self.line_editor.close()
            self.line_editor.deleteLater()
        self.line_editor = LineEditorWidget()
        self.line_editor.accepted.connect(self.updateLine)
        if self.gm.linewidth < 1:
            self.gm.linewidth = 1
        line_obj = vcs.createline(ltype=self.gm.line, color=self.gm.linecolor, width=self.gm.linewidth)
        self.line_editor.setLineObject(line_obj)
        self.line_editor.raise_()
        self.line_editor.show()

    def updateMarker(self, name):
        self.gm.marker = self.marker_editor.object.type[0]
        self.gm.markercolor = self.marker_editor.object.color[0]
        self.gm.markersize = self.marker_editor.object.size[0]

    def updateLine(self, name):
        self.gm.line = self.line_editor.object.type[0]
        self.gm.linecolor = self.line_editor.object.color[0]
        self.gm.linewidth = self.line_editor.object.width[0]

    def flipGraph(self, state):
        if state == QtCore.Qt.Checked:
            self.gm.flip = True
        elif state == QtCore.Qt.Unchecked:
            self.gm.flip = False

    @property
    def gm(self):
        """GM property."""
        return self._gm

    @gm.setter
    def gm(self, value):
        """GM setter."""
        self._gm = value
        self.flip_check.setChecked(value.flip)
