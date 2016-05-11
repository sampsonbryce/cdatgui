from PySide import QtCore, QtGui
from functools import partial

from cdatgui.editors.secondary.editor.line import LineEditorWidget
from cdatgui.bases.window_widget import BaseOkWindowWidget
from cdatgui.bases.dynamic_grid_layout import DynamicGridLayout
import vcs
from cdatgui.vcsmodel import get_lines
from cdatgui.bases.vcs_elements_dialog import VcsElementsDialog, VcsElementsValidator


class MultiLineEditor(BaseOkWindowWidget):
    def __init__(self):
        super(MultiLineEditor, self).__init__()
        self.isoline_model = None
        self.line_editor = None
        self.line_combos = []
        self.dynamic_grid = DynamicGridLayout(400)
        self.vertical_layout.insertLayout(0, self.dynamic_grid)
        self.setWindowTitle("Edit Lines")
        self.resize(300, self.height())

    def setObject(self, object, *args):
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
            line_label = QtGui.QLabel(str(lev))

            line_combo = QtGui.QComboBox()
            line_combo.setModel(get_lines())

            # set to current line
            item = self.isoline_model.line[ind]
            line_combo.setCurrentIndex(get_lines().elements.index(item))
            self.line_combos.append(line_combo)

            edit_line = QtGui.QPushButton('Edit Line')
            edit_line.clicked.connect(partial(self.editLine, ind))

            line_combo.currentIndexChanged.connect(partial(self.changeLine, ind))

            # add everything to layout
            row.addWidget(line_label)
            row.addWidget(line_combo)
            row.addWidget(edit_line)

            row_widget = QtGui.QWidget()
            row_widget.setLayout(row)
            widgets.append(row_widget)

        self.dynamic_grid.addNewWidgets(widgets)

    def editLine(self, index):
        if self.line_editor:
            self.line_editor.close()
            self.line_editor.deleteLater()
        self.line_editor = LineEditorWidget()
        dialog = VcsElementsDialog('line')
        dialog.setValidator(VcsElementsValidator())
        self.line_editor.setSaveDialog(dialog)

        line = self.isoline_model.line[index]
        line_obj = vcs.getline(line)

        self.line_editor.setLineObject(line_obj)
        self.line_editor.saved.connect(partial(self.update, index))

        self.line_editor.show()
        self.line_editor.raise_()

    def changeLine(self, row_index, combo_index):
        """Changed line to an already existing line in the line model"""
        self.isoline_model.line[row_index] = get_lines().elements[combo_index]

    def update(self, index, name):
        """Updated line from line editor"""
        self.isoline_model.line[index] = str(name)
        self.line_combos[index].setCurrentIndex(self.line_combos[index].findText(name))

    def accept(self):
        self.updateGM()
        self.accepted.emit()
        self.close()

    def updateGM(self):
        colors = []
        widths = []
        for line in self.isoline_model.line:
            colors.append(vcs.getline(line).color[0])
            widths.append(vcs.getline(line).width[0])

        self.isoline_model._gm.linecolors = colors
        self.isoline_model._gm.linewidths = widths
