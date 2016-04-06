from PySide import QtGui, QtCore
import vcs
from cdatgui.utils import icon
from cdatgui.vcsmodel import get_lines, get_textstyles
active, inactive, toggle_icon = None, None, None

def initmod():
    global active, inactive, toggle_icon
    if None in (active, inactive, toggle_icon):
        active = icon("active_eye.png")
        inactive = icon("inactive_eye.png")

        toggle_icon = QtGui.QIcon()
        sizes = active.availableSizes()
        toggle_icon.addPixmap(active.pixmap(sizes[0]), QtGui.QIcon.Normal, QtGui.QIcon.On)
        toggle_icon.addPixmap(inactive.pixmap(sizes[0]), QtGui.QIcon.Normal, QtGui.QIcon.Off)

def axis_name(axis, num):
    if axis.lower() == "y":
        if num == 1:
            return "Left Y Axis"
        else:
            return "Right Y Axis"
    if num == 1:
        return "Bottom X Axis"
    else:
        return "Top X Axis"


class AxisLabelEditor(QtGui.QWidget):
    def __init__(self, parent=None):
        super(AxisLabelEditor, self).__init__(parent=parent)
        initmod()
        self.member = None

        self.hide_button = QtGui.QPushButton(toggle_icon, u"")
        self.hide_button.setCheckable(True)
        self.hide_button.clicked.connect(self.hideLabels)

        self.text_chooser = QtGui.QComboBox()
        self.text_chooser.setModel(get_textstyles())
        self.text_chooser.currentIndexChanged[str].connect(self.setTextStyle)

        edit_button = QtGui.QPushButton("Edit")
        edit_button.clicked.connect(self.edit_text)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.hide_button)
        layout.addWidget(self.text_chooser)
        layout.addWidget(edit_button)
        self.setLayout(layout)

    def setMember(self, member):
        self.hide_button.setChecked(member.priority > 0)
        self.text_chooser.setCurrentIndex(self.text_chooser.findText(member.texttable))
        self.member = member

    def edit_text(self):
        pass

    def setTextStyle(self, textstyle):
        pass

    def hideLabels(self):
        pass


class TickEditor(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TickEditor, self).__init__(parent=parent)
        initmod()

        self.member = None

        self.hide_button = QtGui.QPushButton(toggle_icon, u"")
        self.hide_button.setCheckable(True)
        self.hide_button.clicked.connect(self.hideTicks)

        self.line_chooser = QtGui.QComboBox()
        self.line_chooser.setModel(get_lines())
        self.line_chooser.currentIndexChanged[str].connect(self.setLineStyle)

        edit_button = QtGui.QPushButton("Edit")
        edit_button.clicked.connect(self.edit_line)

        top_widgets = QtGui.QHBoxLayout()
        top_widgets.addWidget(self.hide_button)
        top_widgets.addWidget(self.line_chooser)
        top_widgets.addWidget(edit_button)

        length_label = QtGui.QLabel("Length:")
        self.length_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.length_slider.setMinimum(0)
        self.length_slider.setMaximum(100)
        self.length_slider.sliderMoved.connect(self.setLength)

        bottom_widgets = QtGui.QHBoxLayout()
        bottom_widgets.addWidget(length_label)
        bottom_widgets.addWidget(self.length_slider)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(top_widgets)
        layout.addLayout(bottom_widgets)
        self.setLayout(layout)

    def setMember(self, member):
        self.member = member
        if hasattr(self.member, "x1"):
            has_x = True
        else:
            has_x = False
        self.hide_button.setChecked(member.priority > 0)
        self.line_chooser.setCurrentIndex(self.line_chooser.findText(member.line))
        if has_x:
            self.length_slider.setValue(int(100 * abs(member.x1 - member.x2)))
        else:
            self.length_slider.setValue(int(100 * abs(member.y1 - member.y2)))

    def setLength(self, value):
        pass

    def hideTicks(self):
        pass

    def edit_line(self):
        pass

    def setLineStyle(self, style):
        pass


class AxisEditor(QtGui.QWidget):
    def __init__(self, axis, num, parent=None):
        super(AxisEditor, self).__init__(parent=parent)
        self.axis = axis
        self.number = num
        self.template = None

        self.name = axis_name(self.axis, self.number)

        layout = QtGui.QFormLayout()

        self.grid_box = QtGui.QCheckBox()
        layout.addRow("Show Grid", self.grid_box)

        self.inset_box = QtGui.QCheckBox()
        layout.addRow("Inset Ticks", self.inset_box)

        self.tick_editor = TickEditor()
        layout.addRow("Ticks", self.tick_editor)
        self.minitick_editor = TickEditor()
        layout.addRow("Miniticks", self.minitick_editor)
        self.label_editor = AxisLabelEditor()
        layout.addRow("Labels", self.label_editor)

        self.setLayout(layout)

    def ticks(self):
        if self.template is not None:
            return getattr(self.template, "{axis}tic{num}".format(axis=self.axis, num=self.number))

    def minticks(self):
        if self.template is not None:
            return getattr(self.template, "{axis}mintic{num}".format(axis=self.axis, num=self.number))

    def labels(self):
        if self.template is not None:
            return getattr(self.template, "{axis}label{num}".format(axis=self.axis, num=self.number))

    def setTemplate(self, tmpl):
        # Sync GUI with template
        self.template = tmpl

        ticks = self.ticks()
        self.tick_editor.setMember(ticks)
        minticks = self.minticks()
        self.minitick_editor.setMember(minticks)
        labels = self.labels()
        self.label_editor.setMember(labels)
