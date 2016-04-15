from PySide import QtGui, QtCore

from cdatgui.editors.model.legend import VCSLegend
from cdatgui.editors.widgets.legend_widget import LegendEditorWidget
from level_editor import LevelEditor
from axis_editor import AxisEditorWidget
from model.vcsaxis import VCSAxis


class GraphicsMethodEditorWidget(QtGui.QWidget):
    """Configures a boxfill graphics method."""

    graphicsMethodUpdated = QtCore.Signal(object)

    def __init__(self, parent=None):
        """Initialize the object."""
        super(GraphicsMethodEditorWidget, self).__init__(parent=parent)
        self._gm = None
        self.var = None
        self.tmpl = None

        self.button_layout = QtGui.QVBoxLayout()
        self.setLayout(self.button_layout)

        self.levels_button = QtGui.QPushButton("Edit Levels")
        self.levels_button.clicked.connect(self.editLevels)
        self.levels_button.setDefault(False)
        self.levels_button.setAutoDefault(False)
        legend_button = QtGui.QPushButton("Edit Legend")
        legend_button.clicked.connect(self.editLegend)
        legend_button.setAutoDefault(False)
        left_axis = QtGui.QPushButton("Edit Left Ticks")
        left_axis.clicked.connect(self.editLeft)
        right_axis = QtGui.QPushButton("Edit Right Ticks")
        right_axis.clicked.connect(self.editRight)
        bottom_axis = QtGui.QPushButton("Edit Bottom Ticks")
        bottom_axis.clicked.connect(self.editBottom)
        top_axis = QtGui.QPushButton("Edit Top Ticks")
        top_axis.clicked.connect(self.editTop)

        self.button_layout.addWidget(self.levels_button)
        self.button_layout.addWidget(legend_button)
        self.button_layout.addWidget(left_axis)
        self.button_layout.addWidget(right_axis)
        self.button_layout.addWidget(top_axis)
        self.button_layout.addWidget(bottom_axis)

        self.level_editor = None
        self.legend_editor = None
        self.axis_editor = None

    def editAxis(self, axis):
        if self.axis_editor is None:
            self.axis_editor = AxisEditorWidget(axis[0])
            self.axis_editor.okPressed.connect(self.updated)
        axis = VCSAxis(self._gm, self.tmpl, axis, self.var)
        self.axis_editor.setAxisObject(axis)
        self.axis_editor.show()
        self.axis_editor.raise_()

    def editLeft(self):
        self.editAxis("y1")

    def editRight(self):
        self.editAxis("y2")

    def editBottom(self):
        self.editAxis("x1")

    def editTop(self):
        self.editAxis("x2")

    def editLevels(self):
        """Edit the levels of this GM."""
        if self.level_editor is None:
            self.level_editor = LevelEditor()
            self.level_editor.levelsUpdated.connect(self.updated)
        self.level_editor.gm = self.gm
        self.level_editor.var = self.var.var
        self.level_editor.show()
        self.level_editor.raise_()

    def updated(self):
        if self.legend_editor is not None:
            self.legend_editor = None
        if self.axis_editor is not None:
            self.axis_editor = None
        if self.level_editor is not None:
            self.level_editor.deleteLater()
            self.level_editor = None
        print "Emitting updated"
        self.graphicsMethodUpdated.emit(self._gm)
        print "Updated"
        # pdb.set_trace()

    @property
    def gm(self):
        """GM property."""
        return self._gm

    @gm.setter
    def gm(self, value):
        """GM setter."""
        self._gm = value

    def editLegend(self):
        if self.legend_editor is None:
            self.legend_editor = LegendEditorWidget()
            self.legend_editor.okPressed.connect(self.updated)
        legend = VCSLegend(self.gm, self.var.var)
        self.legend_editor.setObject(legend)
        self.legend_editor.show()
        self.legend_editor

