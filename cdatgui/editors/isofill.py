from PySide import QtGui, QtCore
from widgets.legend_widget import LegendEditorWidget
from model.legend import VCSLegend
from .graphics_method_editor import GraphicsMethodEditorWidget


class IsofillEditor(GraphicsMethodEditorWidget):
    """Configures a boxfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(IsofillEditor, self).__init__(parent=parent)

        legend_button = QtGui.QPushButton("Edit Legend")
        legend_button.clicked.connect(self.editLegend)

        self.button_layout.insertWidget(1, legend_button)

    def editLegend(self):
        if self.legend_editor is None:
            self.legend_editor = LegendEditorWidget()
            print "disabling start and end color widgets."
            # self.legend_editor.end_color_widget.setEnabled(False)
            # self.legend_editor.start_color_widget.setEnabled(False)
            self.legend_editor.okPressed.connect(self.updated)
        legend = VCSLegend(self.gm, self.var.var)
        self.legend_editor.setObject(legend)
        self.legend_editor.show()
        self.legend_editor.raise_()