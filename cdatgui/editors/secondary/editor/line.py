from PySide import QtGui, QtCore
from cdatgui.bases.window_widget import BaseSaveWindowWidget
from cdatgui.editors.secondary.preview.line import LinePreviewWidget
import vcs
from cdatgui.vcsmodel import get_lines


class LineEditorWidget(BaseSaveWindowWidget):
    saved = QtCore.Signal(str)

    def __init__(self):
        super(LineEditorWidget, self).__init__()
        self.setPreview(LinePreviewWidget())
        self.accepted.connect(self.saveNewLine)
        self.orig_name = None
        self.newline_name = None

        # create labels
        type_label = QtGui.QLabel("Type:")
        color_label = QtGui.QLabel("Color:")
        width_label = QtGui.QLabel("Width:")

        row = QtGui.QHBoxLayout()

        # create type combo box
        self.type_box = QtGui.QComboBox()
        self.type_box.addItems(["solid", "dash", "dot", "dash-dot", "long-dash"])
        self.type_box.currentIndexChanged[str].connect(self.updateType)

        # create color spin box
        self.color_box = QtGui.QSpinBox()
        self.color_box.setRange(0, 255)
        self.color_box.valueChanged.connect(self.updateColor)

        # create color spin box
        self.width_box = QtGui.QSpinBox()
        self.width_box.setRange(1, 300)
        self.width_box.valueChanged.connect(self.updateWidth)

        row.addWidget(type_label)
        row.addWidget(self.type_box)

        row.addWidget(color_label)
        row.addWidget(self.color_box)

        row.addWidget(width_label)
        row.addWidget(self.width_box)

        self.vertical_layout.insertLayout(1, row)

    def setLineObject(self, line_obj):
        self.setWindowTitle('Edit {0} line'.format(line_obj.name))
        self.orig_name = line_obj.name

        if line_obj.name == 'default':
            self.save_button.setEnabled(False)

        line_obj = vcs.createline(source=line_obj.name)
        self.newline_name = line_obj.name

        self.object = line_obj
        self.preview.setLineObject(self.object)

        self.type_box.setCurrentIndex(self.type_box.findText(self.object.type[0]))
        self.color_box.setValue(self.object.color[0])
        self.width_box.setValue(self.object.width[0])

    def updateType(self, cur_item):
        self.object.type = [str(cur_item)]
        self.preview.update()

    def updateColor(self, color):
        self.object.color = [color]
        self.preview.update()

    def updateWidth(self, width):
        self.object.width = [width]
        self.preview.update()

    def saveNewLine(self, name):
        name = str(name)

        if name == self.newline_name:
            if self.orig_name in vcs.elements['line']:
                del vcs.elements['line'][self.orig_name]

            vcs.createline(self.orig_name, source=name)
            get_lines().updated(self.orig_name)
            self.saved.emit(self.orig_name)
        else:
            if name in vcs.elements['line']:
                del vcs.elements['line'][name]
            vcs.createline(name, source=self.newline_name)
            get_lines().updated(name)
            self.saved.emit(name)

    def close(self):
        if self.newline_name in vcs.elements['line']:
            del vcs.elements['line'][self.newline_name]
        super(LineEditorWidget, self).close()
