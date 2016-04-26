from PySide import QtCore, QtGui
from functools import partial

from cdatgui.editors.secondary.editor.line import LineEditorWidget
from cdatgui.bases.window_widget import BaseOkWindowWidget
from cdatgui.bases.dynamic_grid_layout import DynamicGridLayout
import vcs
from cdatgui.vcsmodel import get_lines
from cdatgui.bases.input_dialog import ValidatingInputDialog


class LineNameDialog(ValidatingInputDialog):
    def save(self):
        print "SAVING"
        if self.textValue() in vcs.elements['line']:
            check = QtGui.QMessageBox.question(self, "Overwrite line?",
                                               "Line {0} already exists. Overwrite?".format(self.textValue()),
                                               buttons=QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
            if check == QtGui.QDialogButtonBox.FirstButton:
                self.close()
                self.accepted.emit()
        else:
            self.close()
            self.accepted.emit()


class LineTextValidator(QtGui.QValidator):
    invalidInput = QtCore.Signal()
    validInput = QtCore.Signal()

    def validate(self, inp, pos):
        inp = inp.strip()
        if not inp or inp == 'default':
            self.invalidInput.emit()
            return QtGui.QValidator.Intermediate

        self.validInput.emit()
        return QtGui.QValidator.Acceptable


class MultiLineEditor(BaseOkWindowWidget):
    def __init__(self):
        super(MultiLineEditor, self).__init__()
        self.isoline_model = None
        self.line_editor = None
        self.line_combos = []
        self.dynamic_grid = DynamicGridLayout(400)
        self.vertical_layout.insertLayout(0, self.dynamic_grid)
        self.setWindowTitle("Edit Lines")

    def setObject(self, object, *args):
        print "SETTING OBJECT"
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
            line_label = QtGui.QLabel("Line:")

            line_combo = QtGui.QComboBox()
            line_combo.setModel(get_lines())
            # must call to adjust values for length of levels before indexing into levels
            lines = self.isoline_model.line
            item = self.isoline_model.line[ind]

            print "LINES", lines
            print "ITEM:", item
            print "ELEMENTS:", get_lines().elements
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
        dialog = LineNameDialog()
        dialog.setValidator(LineTextValidator())
        self.line_editor.setSaveDialog(dialog)

        line = self.isoline_model.line[index]
        line_obj = vcs.getline(line)

        self.line_editor.setLineObject(line_obj)
        self.line_editor.saved.connect(partial(self.update, index))

        self.line_editor.show()
        self.line_editor.raise_()

    def changeLine(self, row_index, combo_index):
        print "ChangeLine, row_i, combo_i", row_index, combo_index
        self.isoline_model.line[row_index] = get_lines().elements[combo_index]

    def update(self, index, name):
        print "UPDATING:", index, name
        self.isoline_model.line[index] = str(name)
        self.line_combos[index].setCurrentIndex(self.line_combos[index].findText(name))

    def okClicked(self):
        self.updateGM()
        self.okPressed.emit()
        self.close()

    def updateGM(self):
        colors = []
        widths = []
        for line in self.isoline_model.line:
            colors.append(vcs.getline(line).color[0])
            widths.append(vcs.getline(line).width[0])

        self.isoline_model._gm.linecolors = colors
        self.isoline_model._gm.linewidths = widths
