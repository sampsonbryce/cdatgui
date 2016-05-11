from PySide import QtCore, QtGui
from functools import partial

from cdatgui.editors.secondary.editor.text import TextStyleEditorWidget
from cdatgui.bases.window_widget import BaseOkWindowWidget
from cdatgui.bases.dynamic_grid_layout import DynamicGridLayout
import vcs
from cdatgui.vcsmodel import get_textstyles
from cdatgui.bases.vcs_elements_dialog import VcsElementsDialog, VcsElementsValidator


class MultiTextEditor(BaseOkWindowWidget):
    def __init__(self):
        super(MultiTextEditor, self).__init__()
        self.isoline_model = None
        self.text_editor = None
        self.text_combos = []
        self.dynamic_grid = DynamicGridLayout(400)
        self.vertical_layout.insertLayout(0, self.dynamic_grid)
        self.setWindowTitle("Edit Texts")
        self.resize(300, self.height())

    def setObject(self, object):
        self.isoline_model = object
        widgets = []

        # clear grid
        grid_widgets = self.dynamic_grid.getWidgets()
        self.dynamic_grid.clearWidgets()

        for widget in grid_widgets:
            self.dynamic_grid.removeWidget(widget)
            widget.deleteLater()

        # repopulate
        for ind, lev in enumerate(self.isoline_model.levels):
            row = QtGui.QHBoxLayout()
            text_label = QtGui.QLabel(str(lev))

            text_combo = QtGui.QComboBox()
            text_combo.setModel(get_textstyles())

            # set to current text
            item = self.isoline_model.text[ind]
            text_combo.setCurrentIndex(get_textstyles().elements.index(item))
            self.text_combos.append(text_combo)

            edit_text = QtGui.QPushButton('Edit Text')
            edit_text.clicked.connect(partial(self.editText, ind))

            text_combo.currentIndexChanged[str].connect(partial(self.changeText, ind))

            # add everything to layout
            row.addWidget(text_label)
            row.addWidget(text_combo)
            row.addWidget(edit_text)

            row_widget = QtGui.QWidget()
            row_widget.setLayout(row)
            widgets.append(row_widget)

        self.dynamic_grid.addNewWidgets(widgets)

    def editText(self, index):
        if self.text_editor:
            self.text_editor.close()
            self.text_editor.deleteLater()
        self.text_editor = TextStyleEditorWidget()
        dialog = VcsElementsDialog('texttable')
        dialog.setValidator(VcsElementsValidator())
        self.text_editor.setSaveDialog(dialog)

        text = self.isoline_model.text[index]
        text_obj = get_textstyles().get_el(text)

        self.text_editor.setTextObject(text_obj)
        self.text_editor.saved.connect(partial(self.update, index))

        self.text_editor.show()
        self.text_editor.raise_()

    def changeText(self, row_index, combo_index):
        self.isoline_model.text[row_index] = get_textstyles().elements[get_textstyles().elements.index(combo_index)]

    def update(self, index, name):
        self.text_combos[index].setCurrentIndex(self.text_combos[index].findText(name))

    def accept(self):
        self.accepted.emit()
        self.close()
