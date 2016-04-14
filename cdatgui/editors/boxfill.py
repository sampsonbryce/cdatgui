from PySide import QtGui, QtCore
from collections import OrderedDict

from widgets.legend_widget import LegendEditorWidget
from model.legend import VCSLegend
from .graphics_method_editor import GraphicsMethodEditorWidget


class BoxfillEditor(GraphicsMethodEditorWidget):
    """Configures a boxfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(BoxfillEditor, self).__init__(parent=parent)

        legend_button = QtGui.QPushButton("Edit Legend")
        legend_button.clicked.connect(self.editLegend)

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
        self.button_layout.insertWidget(2, legend_button)

    def editLegend(self):
        if self.legend_editor is None:
            print "launching boxfill legend editor"
            self.legend_editor = LegendEditorWidget()
            self.legend_editor.okPressed.connect(self.updated)
        legend = VCSLegend(self.gm, self.var.var)
        self.legend_editor.setObject(legend)
        self.legend_editor.show()
        self.legend_editor.raise_()

    @property
    def gm(self):
        """GM property."""
        return self._gm

    @gm.setter
    def gm(self, value):
        self._gm = value
        type_real_vals = self.boxfill_types.values()
        index = type_real_vals.index(value.boxfill_type)
        self.type_group.buttons()[index].setChecked(True)

    def setBoxfillType(self, radio):
        """Take in a radio button and set the GM boxfill_type."""
        box_type = self.boxfill_types[radio.text()]
        self._gm.boxfill_type = box_type
        self.graphicsMethodUpdated.emit(self._gm)
