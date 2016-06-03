from PySide import QtGui, QtCore
from collections import OrderedDict

import numpy, vcs

from .graphics_method_editor import GraphicsMethodEditorWidget


class BoxfillEditor(GraphicsMethodEditorWidget):
    """Configures a boxfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(BoxfillEditor, self).__init__(parent=parent)

        self.orig_type = None
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

        self.type_group.buttonClicked.connect(self.setBoxfillType)

        self.button_layout.insertLayout(0, button_layout)
        self.levels_button.setEnabled(False)

        self.graphicsMethodUpdated.connect(self.updateLegendButton)

    def updateLegendButton(self):
        levs = self._gm.getlevels(*vcs.minmax(self.var))
        if len(levs) == 2 and numpy.allclose(levs, [1e+20] * 2):
            self.legend_button.setEnabled(False)
        else:
            self.legend_button.setEnabled(True)

    @property
    def gm(self):
        """GM property."""
        return self._gm

    @gm.setter
    def gm(self, value):
        self._gm = value
        self.orig_type = self._gm.boxfill_type
        type_real_vals = self.boxfill_types.values()
        index = type_real_vals.index(value.boxfill_type)
        button = self.type_group.buttons()[index]
        button.click()
        self.setBoxfillType(button)

    def setBoxfillType(self, radio):
        """Take in a radio button and set the GM boxfill_type."""
        box_type = self.boxfill_types[radio.text()]
        self._gm.boxfill_type = box_type

        if radio.text() == 'Custom':
            self.levels_button.setEnabled(True)
            self.updateLegendButton()
        else:
            self.levels_button.setEnabled(False)


