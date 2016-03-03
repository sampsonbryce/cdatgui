from PySide import QtGui, QtCore
from collections import OrderedDict
from level_editor import LevelEditor


class BoxfillEditor(QtGui.QWidget):
    """Configures a boxfill graphics method."""

    graphicsMethodUpdated = QtCore.Signal(object)

    def __init__(self, parent=None):
        """Initialize the object."""
        super(BoxfillEditor, self).__init__(parent=parent)
        self._gm = None

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
        layout.addWidget(levels_button)
        self.level_editor = None
        self.type_group.buttonClicked.connect(self.setBoxfillType)

    def editLevels(self):
        """Edit the levels of this GM."""
        if self.level_editor is None:
            self.level_editor = LevelEditor()
            self.level_editor.levelsUpdated.connect(self.appliedLevels)
        self.level_editor.gm = self.gm
        self.level_editor.var = self.parent().plot.variables[0]
        self.level_editor.show()
        self.level_editor.raise_()

    def appliedLevels(self):
        """Finished editing levels."""
        self.graphicsMethodUpdated.emit(self._gm)
        self.level_editor.levelsUpdated.disconnect(self.appliedLevels)
        self.level_editor.hide()
        self.level_editor.deleteLater()
        self.level_editor = None

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
