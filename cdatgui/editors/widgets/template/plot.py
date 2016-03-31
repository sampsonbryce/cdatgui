from PySide import QtGui, QtCore
from cdatgui.utils import icon
import vcs
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


class BoxEditor(QtGui.QWidget):
    boxEdited = QtCore.Signal(object)
    moveBox = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(BoxEditor, self).__init__(parent=parent)
        initmod()
        self.member = None
        self.outline = None
        self.template = None
        layout = QtGui.QFormLayout()

        buttons = QtGui.QHBoxLayout()
        self.move_button = QtGui.QPushButton(u"Move")
        buttons.addWidget(self.move_button)
        self.hide_button = QtGui.QPushButton(toggle_icon, u"")
        self.hide_button.setCheckable(True)
        self.hide_button.clicked.connect(self.hideMember)
        buttons.addWidget(self.hide_button)
        layout.addRow(buttons)

        self.width_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.width_slider.setMinimum(0)
        self.width_slider.setMaximum(100)
        self.width_slider.valueChanged.connect(self.setBoxWidth)
        layout.addRow("Width", self.width_slider)

        self.height_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.height_slider.setMinimum(0)
        self.height_slider.setMaximum(100)
        self.height_slider.valueChanged.connect(self.setBoxHeight)
        layout.addRow("Height", self.height_slider)

        outline_actions = QtGui.QHBoxLayout()
        self.outline_hide = QtGui.QPushButton(toggle_icon, u"")
        self.outline_hide.setCheckable(True)
        self.outline_hide.clicked.connect(self.hideOutline)
        self.outline_style = QtGui.QComboBox()
        for l in vcs.listelements("line"):
            if l[:2] == "__":
                continue
            self.outline_style.addItem(l)
        outline_edit = QtGui.QPushButton("Edit")
        outline_actions.addWidget(self.outline_hide)
        outline_actions.addWidget(self.outline_style)
        outline_actions.addWidget(outline_edit)

        layout.addRow("Outline", outline_actions)
        self.setLayout(layout)

    def hideMember(self):
        if self.hide_button.isChecked():
            self.member.priority = 1
        else:
            self.member.priority = 0
        self.boxEdited.emit(self.member)

    def hideOutline(self):
        if self.outline_hide.isChecked():
            self.outline.priority = 1
        else:
            self.outline.priority = 0
        self.boxEdited.emit(self.member)

    def setTemplate(self, template):
        self.hide_button.setChecked(self.member.priority > 0)
        self.width_slider.setValue(abs(self.member.x2 - self.member.x1))
        self.height_slider.setValue(abs(self.member.y2 - self.member.y1))
        self.outline_style.setCurrentIndex(self.outline_style.findText(self.outline.line))
        self.outline_hide.setChecked(self.outline.priority > 0)
        self.template = template

    def setBoxWidth(self, val, buffer=0):
        self.member.x2 = self.member.x1 + (1 - self.member.x1 - buffer) * val / 100.
        self.outline.x2 = self.member.x2
        self.boxEdited.emit(self.member)

    def setBoxHeight(self, val, buffer=0):
        self.member.y2 = self.member.y1 + (1 - self.member.y1 - buffer) * val / 100.
        self.outline.y2 = self.member.y2
        self.boxEdited.emit(self.member)


class DataEditor(BoxEditor):
    def setTemplate(self, template):
        self.member = template.data
        self.outline = template.box1
        super(DataEditor, self).setTemplate(template)

    def setBoxWidth(self, val):
        block = self.blockSignals(True)

        tic_len = self.template.ytic2.x2 - self.template.ytic2.x1
        mintic_len = self.template.ymintic2.x2 - self.template.ymintic2.x1
        # Prevent tics from going offscreen
        buffer = max(tic_len, mintic_len)
        super(DataEditor, self).setBoxWidth(val, buffer=buffer)
        self.blockSignals(block)
        # Also adjust ytic2/ymintic2

        self.template.ytic2.x1 = self.outline.x2
        self.template.ytic2.x2 = self.template.ytic2.x1 + tic_len

        self.template.ymintic2.x1 = self.outline.x2
        self.template.ymintic2.x2 = self.template.ymintic2.x1 + mintic_len
        self.boxEdited.emit(self.member)

    def setBoxHeight(self, val):
        block = self.blockSignals(True)
        tic_len = self.template.xtic2.y2 - self.template.xtic2.y1
        mintic_len = self.template.xmintic2.y2 - self.template.xmintic2.y1
        buffer = max(tic_len, mintic_len)
        super(DataEditor, self).setBoxHeight(val, buffer=buffer)
        self.blockSignals(block)
        # Also adjust xtic2/xmintic2
        self.template.xtic2.y1 = self.outline.y2
        self.template.xtic2.y2 = self.template.xtic2.y1 + tic_len
        self.template.xmintic2.y1 = self.outline.y2
        self.template.xmintic2.y2 = self.template.xmintic2.y1 + mintic_len
        self.boxEdited.emit(self.member)

class LegendEditor(BoxEditor):
    def setTemplate(self, template):
        self.member = template.legend
        self.outline = template.legend


