from PySide import QtGui, QtCore
from collections import OrderedDict
from level_editor import LevelEditor
from widgets.legend_widget import LegendEditorWidget
from model.legend import VCSLegend
from axis_editor import AxisEditorWidget
from model.vcsaxis import VCSAxis


class BoxfillEditor(QtGui.QWidget):
    """Configures a boxfill graphics method."""

    graphicsMethodUpdated = QtCore.Signal(object)

    def __init__(self, parent=None):
        """Initialize the object."""
        super(BoxfillEditor, self).__init__(parent=parent)
        self._gm = None
        self.var = None
        self.tmpl = None

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.boxfill_types = OrderedDict(
            Linear="linear",
            Logarithmic="log10",
            Custom="custom"
        )

        button_layout = QtGui.QHBoxLayout()
        label = QtGui.QLabel("Levels:")
        button_layout.addWidget(label)
        self.type_group = QtGui.QButtonGroup()
        for label in self.boxfill_types:
            radiobutton = QtGui.QRadioButton(label)
            button_layout.addWidget(radiobutton)
            self.type_group.addButton(radiobutton)

        layout.addLayout(button_layout)

        levels_button = QtGui.QPushButton("Edit Levels")
        levels_button.clicked.connect(self.editLevels)
        legend_button = QtGui.QPushButton("Edit Legend")
        legend_button.clicked.connect(self.editLegend)

        left_axis = QtGui.QPushButton("Edit Left Ticks")
        left_axis.clicked.connect(self.editLeft)
        right_axis = QtGui.QPushButton("Edit Right Ticks")
        right_axis.clicked.connect(self.editRight)
        bottom_axis = QtGui.QPushButton("Edit Bottom Ticks")
        bottom_axis.clicked.connect(self.editBottom)
        top_axis = QtGui.QPushButton("Edit Top Ticks")
        top_axis.clicked.connect(self.editTop)

        layout.addWidget(levels_button)
        layout.addWidget(legend_button)
        layout.addWidget(left_axis)
        layout.addWidget(right_axis)
        layout.addWidget(top_axis)
        layout.addWidget(bottom_axis)

        self.level_editor = None
        self.legend_editor = None
        self.axis_editor = None
        self.type_group.buttonClicked.connect(self.setBoxfillType)

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

    def editLegend(self):
        if self.legend_editor is None:
            self.legend_editor = LegendEditorWidget()
            self.legend_editor.okPressed.connect(self.updated)
        legend = VCSLegend(self.gm, self.var.var)
        self.legend_editor.setObject(legend)
        self.legend_editor.show()
        self.legend_editor.raise_()

    def updated(self):
        if self.legend_editor is not None:
            self.legend_editor = None
        if self.axis_editor is not None:
            self.axis_editor = None
        if self.level_editor is not None:
            self.level_editor = None
        print "Emitting updated"
        self.graphicsMethodUpdated.emit(self._gm)
        print "Updated"

    @property
    def gm(self):
        """GM property."""
        return self._gm

    @gm.setter
    def gm(self, value):
        """GM setter."""
        self._gm = value
        type_real_vals = self.boxfill_types.values()
        index = type_real_vals.index(value.boxfill_type)
        self.type_group.buttons()[index].setChecked(True)

    def setBoxfillType(self, radio):
        """Take in a radio button and set the GM boxfill_type."""
        box_type = self.boxfill_types[radio.text()]
        self._gm.boxfill_type = box_type
        self.graphicsMethodUpdated.emit(self._gm)
