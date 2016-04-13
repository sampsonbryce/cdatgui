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
    labelsUpdated = QtCore.Signal()
    editTextStyle = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AxisLabelEditor, self).__init__(parent=parent)
        initmod()
        self.member = None
        self.template = None

        self.hide_button = QtGui.QPushButton(toggle_icon, u"")
        self.hide_button.setCheckable(True)
        self.hide_button.clicked.connect(self.hideLabels)

        self.inset = False
        self.text_chooser = QtGui.QComboBox()
        self.text_chooser.setModel(get_textstyles())
        self.text_chooser.currentIndexChanged[str].connect(self.setTextStyle)

        edit_button = QtGui.QPushButton("Edit")
        edit_button.clicked.connect(self.edit_text)

        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(self.hide_button)
        hlayout.addWidget(self.text_chooser)
        hlayout.addWidget(edit_button)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(hlayout)

        slide_layout = QtGui.QHBoxLayout()

        distance_label = QtGui.QLabel("Distance:")
        self.distance_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.distance_slider.setMinimum(0)
        self.distance_slider.setMaximum(100)
        self.distance_slider.sliderMoved.connect(self.setDistance)

        slide_layout.addWidget(distance_label)
        slide_layout.addWidget(self.distance_slider)

        layout.addLayout(slide_layout)

        self.setLayout(layout)

    def isYAxis(self):
        return self.member.member[0] == "y"

    def isFirstAxis(self):
        return self.member.member[-1] == "1"

    def setDistance(self, value=None):
        if value is None:
            value = self.distance_slider.value()
        direction = -1 if self.inset else 1
        if self.isFirstAxis():
            direction *= -1
        # Have to distance oneself from the appropriate end
        min_or_max = min if direction < 0 else max
        if self.isYAxis():
            if self.isFirstAxis():
                axis = min_or_max(self.template.ytic1.x1, self.template.ytic1.x2)
            else:
                axis = min_or_max(self.template.ytic2.x1, self.template.ytic2.x2)
            self.member.x = axis + direction * value / 100.
        else:
            if self.isFirstAxis():
                axis = min_or_max(self.template.xtic1.y1, self.template.xtic1.y2)
            else:
                axis = min_or_max(self.template.xtic2.y1, self.template.xtic2.y2)
            self.member.y = axis + direction * value / 100.
        self.labelsUpdated.emit()

    def setInset(self, inset):
        self.inset = inset
        self.setDistance()

    def setMember(self, member, template):
        self.template = template
        self.hide_button.setChecked(member.priority > 0)
        self.text_chooser.setCurrentIndex(self.text_chooser.findText(member.texttable))
        self.member = member

        if self.isYAxis():
            axis = self.template.ytic1 if self.isFirstAxis() else self.template.ytic2
            distance_min = member.x - min(axis.x1, axis.x2)
            distance_max = member.x - max(axis.x1, axis.x2)
        else:
            axis = self.template.xtic1 if self.isFirstAxis() else self.template.xtic2
            distance_min = member.y - min(axis.y1, axis.y2)
            distance_max = member.y - max(axis.y1, axis.y2)

        if distance_min < 0:
            # it's to the left
            distance = abs(distance_min)
        elif distance_max > 0:
            # it's to the right
            distance = distance_max
        else:
            # give up and default to 0
            distance = 0

        block = self.blockSignals(True)
        self.setDistance(int(distance * 100))
        self.blockSignals(block)

    def edit_text(self):
        self.editTextStyle.emit(self.text_chooser.currentText())

    def setTextStyle(self, textstyle):
        #self.member.texttable = textstyle
        #self.member.textorientation = textstyle
        pass
        #self.labelsUpdated.emit()

    def hideLabels(self):
        if self.hide_button.isChecked():
            self.member.priority = 1
        else:
            self.member.priority = 0
        self.labelsUpdated.emit()


class TickEditor(QtGui.QWidget):
    ticksUpdated = QtCore.Signal()
    editLine = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(TickEditor, self).__init__(parent=parent)
        initmod()

        self.member = None
        self.template = None
        self.inset = False
        self.grid = False

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

    def setMember(self, member, template):
        self.member = member
        self.template = template
        self.hide_button.setChecked(member.priority > 0)
        self.line_chooser.setCurrentIndex(self.line_chooser.findText(member.line))
        if self.isYAxis():
            self.length_slider.setValue(int(100 * abs(member.x1 - member.x2)))
        else:
            self.length_slider.setValue(int(100 * abs(member.y1 - member.y2)))

    def isYAxis(self):
        return self.member.member[0] == "y"

    def isFirstAxis(self):
        return self.member.member[-1] == "1"

    def length(self):
        if self.isYAxis():
            return abs(self.member.x2 - self.member.x1)
        else:
            return abs(self.member.y2 - self.member.y1)

    def setGrid(self, grid):
        self.grid = grid
        # Update lengths
        self.placeTicks()

    def setInset(self, inset):
        self.inset = inset
        self.placeTicks()

    def setLength(self, value):
        self.placeTicks(length=value/100.)

    def placeTicks(self, length=None):
        direction = -1 if self.isFirstAxis() else 1

        if self.inset:
            direction *= -1

        if length is None:
            length = self.length()

        if self.isYAxis():
            if self.isFirstAxis():
                axis = min(self.template.data.x1, self.template.data.x2)
            else:
                axis = max(self.template.data.x1, self.template.data.x2)
            self.member.x1 = axis
            self.member.x2 = axis + direction * length
        else:
            if self.isFirstAxis():
                axis = min(self.template.data.y1, self.template.data.y2)
            else:
                axis = max(self.template.data.y1, self.template.data.y2)
            self.member.y1 = axis
            self.member.y2 = axis + direction * length
        self.ticksUpdated.emit()

    def hideTicks(self):
        self.member.priority = 1 if self.hide_button.isChecked() else 0
        self.ticksUpdated.emit()

    def edit_line(self):
        pass

    def setLineStyle(self, style):
        pass


class AxisEditor(QtGui.QWidget):
    axisUpdated = QtCore.Signal()
    editLine = QtCore.Signal(str)
    editTextStyle = QtCore.Signal(str)

    def __init__(self, axis, num, parent=None):
        super(AxisEditor, self).__init__(parent=parent)
        self.axis = axis
        self.number = num
        self.template = None

        self.name = axis_name(self.axis, self.number)

        layout = QtGui.QFormLayout()

        self.grid_box = QtGui.QCheckBox()
        self.grid_box.stateChanged.connect(self.toggleGrid)
        layout.addRow("Show Grid", self.grid_box)

        self.inset_box = QtGui.QCheckBox()
        self.inset_box.stateChanged.connect(self.toggleInset)
        layout.addRow("Inset Ticks", self.inset_box)

        self.tick_editor = TickEditor()
        self.tick_editor.ticksUpdated.connect(self.adjustedTicks)
        layout.addRow("Ticks", self.tick_editor)

        self.minitick_editor = TickEditor()
        layout.addRow("Miniticks", self.minitick_editor)
        self.label_editor = AxisLabelEditor()
        self.label_editor.labelsUpdated.connect(self.axisUpdated.emit)
        layout.addRow("Labels", self.label_editor)

        self.setLayout(layout)

    def adjustedTicks(self):
        self.label_editor.setDistance()

    def toggleGrid(self, state):
        self.tick_editor.setGrid(self.grid_box.isChecked())
        self.minitick_editor.setGrid(self.grid_box.isChecked())
        self.axisUpdated.emit()

    def toggleInset(self, state):
        # Prevent double preview updates
        block = self.blockSignals(True)
        self.tick_editor.setInset(self.inset_box.isChecked())
        self.minitick_editor.setInset(self.inset_box.isChecked())
        self.label_editor.setInset(self.inset_box.isChecked())
        self.blockSignals(block)
        self.axisUpdated.emit()

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
        self.tick_editor.setMember(ticks, self.template)
        minticks = self.minticks()
        self.minitick_editor.setMember(minticks, self.template)
        labels = self.labels()
        self.label_editor.setMember(labels, self.template)
