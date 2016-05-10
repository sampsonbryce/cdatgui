from PySide import QtGui, QtCore

from .graphics_method_editor import GraphicsMethodEditorWidget
from .widgets.multi_line_editor import MultiLineEditor
from .model.isoline_model import IsolineModel
from .widgets.multi_text_editor import MultiTextEditor


class IsolineEditor(GraphicsMethodEditorWidget):
    """Configures a meshfill graphics method."""

    def __init__(self, parent=None):
        """Initialize the object."""
        super(IsolineEditor, self).__init__(parent=parent)
        self._var = None

        self.edit_label_button = QtGui.QPushButton('Edit Labels')
        self.edit_label_button.clicked.connect(self.editText)

        edit_line_button = QtGui.QPushButton('Edit Lines')
        edit_line_button.clicked.connect(self.editLines)

        self.label_check = QtGui.QCheckBox()
        self.label_check.stateChanged.connect(self.updateLabel)

        label = QtGui.QLabel('Label')

        label_layout = QtGui.QHBoxLayout()
        label_layout.addWidget(label)
        label_layout.addWidget(self.label_check)
        label_layout.addStretch(1)

        self.button_layout.insertWidget(0, edit_line_button)
        self.button_layout.insertWidget(0, self.edit_label_button)
        self.button_layout.insertLayout(0, label_layout)

        self.text_edit_widget = None
        self.line_edit_widget = None

        self.legend_button.setEnabled(False)
        self.legend_button.hide()

    def editText(self):
        if self.text_edit_widget:
            self.text_edit_widget.close()
            self.text_edit_widget.deleteLater()
        self.text_edit_widget = MultiTextEditor()
        self.text_edit_widget.setObject(IsolineModel(self._gm, self._var))
        self.text_edit_widget.show()
        self.text_edit_widget.raise_()

    def editLines(self):
        if self.line_edit_widget:
            self.line_edit_widget.close()
            self.line_edit_widget.deleteLater()
        self.line_edit_widget = MultiLineEditor()
        self.line_edit_widget.setObject(IsolineModel(self._gm, self._var))
        self.line_edit_widget.show()
        self.line_edit_widget.raise_()

    def updateLabel(self, state):
        if state == QtCore.Qt.Unchecked:
            self._gm.label = False
            self.edit_label_button.setEnabled(False)
        elif state == QtCore.Qt.Checked:
            self._gm.label = True
            self.edit_label_button.setEnabled(True)

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, v):
        self._var = v

    @property
    def gm(self):
        """GM property."""
        return self._gm

    @gm.setter
    def gm(self, value):
        """GM setter."""
        self._gm = value
        self.label_check.setChecked(self._gm.label)
        self.edit_label_button.setEnabled(self._gm.label)

