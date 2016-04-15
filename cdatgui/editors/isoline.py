from PySide import QtGui

from .graphics_method_editor import GraphicsMethodEditorWidget
from .secondary.editor.text import TextStyleEditorWidget


class IsolineEditor(GraphicsMethodEditorWidget):
    """Configures a meshfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(IsolineEditor, self).__init__(parent=parent)

        edit_text_button = QtGui.QPushButton('Edit Text')
        edit_text_button.clicked.connect(self.editText)
        self.button_layout.insertWidget(0, edit_text_button)

        self.text_edit_widget = None

    def editText(self):
        if not self.text_edit_widget:
            self.text_edit_widget = TextStyleEditorWidget()
            self.text_edit_widget.show()
            self.text_edit_widget._raise()

    def editLine(self):
        if not self.line_edit_widget:
            # self.line_edit_widget = Line()
            self.line_edit_widget.show()
            self.line_edit_widget._raise()
