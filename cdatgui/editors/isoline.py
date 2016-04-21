from PySide import QtGui

from .graphics_method_editor import GraphicsMethodEditorWidget
from .secondary.editor.text import TextStyleEditorWidget
from .widgets.multi_line_editor import MultiLineEditor
from .model.line_model import LineModel


class IsolineEditor(GraphicsMethodEditorWidget):
    """Configures a meshfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(IsolineEditor, self).__init__(parent=parent)
        self._var = None

        edit_text_button = QtGui.QPushButton('Edit Text')
        edit_text_button.clicked.connect(self.editText)

        edit_line_button = QtGui.QPushButton('Edit Lines')
        edit_line_button.clicked.connect(self.editLines)

        self.button_layout.insertWidget(0, edit_text_button)
        self.button_layout.insertWidget(0, edit_line_button)

        self.text_edit_widget = None
        self.line_edit_widget = None

    def editText(self):
        if not self.text_edit_widget:
            self.text_edit_widget = TextStyleEditorWidget()
            self.text_edit_widget.show()
            self.text_edit_widget.raise_()

    def editLines(self):
        if self.line_edit_widget:
            self.line_edit_widget.close()
            self.line_edit_widget.deleteLater()
        self.line_edit_widget = MultiLineEditor()
        self.line_edit_widget.setObject(LineModel(self._gm, self._var))
        self.line_edit_widget.okPressed.connect(self.update)
        self.line_edit_widget.show()
        self.line_edit_widget.raise_()

    def update(self):
        # self._gm.list()
        pass

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, v):
        self._var = v
