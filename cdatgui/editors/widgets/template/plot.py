from PySide import QtGui, QtCore
from cdatgui.utils import icon
from cdatgui.vcsmodel import get_lines
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
    boxEdited = QtCore.Signal()
    # X, Y, callback
    moveBox = QtCore.Signal(float, float, object)
    editStyle = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(BoxEditor, self).__init__(parent=parent)
        initmod()
        self.member = None
        self.outline = None
        self.template = None
        layout = QtGui.QFormLayout()

        buttons = QtGui.QHBoxLayout()
        self.move_button = QtGui.QPushButton(u"Move")
        self.move_button.clicked.connect(self.clickedMove)
        buttons.addWidget(self.move_button)
        self.hide_button = QtGui.QPushButton(toggle_icon, u"")
        self.hide_button.setCheckable(True)
        self.hide_button.clicked.connect(self.hideMember)
        buttons.addWidget(self.hide_button)
        layout.addRow(buttons)

        self.width_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.width_slider.setMinimum(0)
        self.width_slider.setMaximum(100)
        self.width_slider.sliderMoved.connect(self.setBoxWidth)
        layout.addRow("Width", self.width_slider)

        self.height_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.height_slider.setMinimum(0)
        self.height_slider.setMaximum(100)
        self.height_slider.sliderMoved.connect(self.setBoxHeight)
        layout.addRow("Height", self.height_slider)

        outline_actions = QtGui.QHBoxLayout()
        self.outline_hide = QtGui.QPushButton(toggle_icon, u"")
        self.outline_hide.setCheckable(True)
        self.outline_hide.clicked.connect(self.hideOutline)
        self.outline_style = QtGui.QComboBox()
        self.outline_style.setModel(get_lines())
        self.outline_style.currentIndexChanged[str].connect(self.setOutlineStyle)
        outline_edit = QtGui.QPushButton("Edit")
        outline_edit.clicked.connect(self.triggerEditStyle)
        outline_actions.addWidget(self.outline_hide)
        outline_actions.addWidget(self.outline_style)
        outline_actions.addWidget(outline_edit)

        layout.addRow("Outline", outline_actions)
        self.setLayout(layout)

    def clickedMove(self):
        self.moveBox.emit(self.x, self.y, self.move)

    def move(self, x, y):
        pass

    def setOutlineStyle(self, style):
        style = str(style)
        self.outline.line = style
        self.boxEdited.emit()

    def triggerEditStyle(self):
        style = str(self.outline_style.currentText())
        self.editStyle.emit(style)

    def hideMember(self):
        if self.hide_button.isChecked():
            self.member.priority = 1
        else:
            self.member.priority = 0
        self.boxEdited.emit()

    def hideOutline(self):
        if self.outline_hide.isChecked():
            self.outline.priority = 1
        else:
            self.outline.priority = 0
        self.boxEdited.emit()

    def setTemplate(self, template):
        block = self.blockSignals(True)
        self.hide_button.setChecked(self.member.priority > 0)
        self.width_slider.setValue(int(100 * abs(self.member.x2 - self.member.x1)))
        self.height_slider.setValue(int(100 * abs(self.member.y2 - self.member.y1)))
        self.outline_style.setCurrentIndex(self.outline_style.findText(self.outline.line))
        self.outline_hide.setChecked(self.outline.priority > 0)
        self.template = template
        self.blockSignals(block)

    def setBoxWidth(self, val, buffer=0):
        self.member.x2 = self.member.x1 + (1 - self.member.x1 - buffer) * val / 100.
        self.outline.x2 = self.member.x2
        self.boxEdited.emit()

    def setBoxHeight(self, val, buffer=0):
        self.member.y2 = self.member.y1 + (1 - self.member.y1 - buffer) * val / 100.
        self.outline.y2 = self.member.y2
        self.boxEdited.emit()

    @property
    def x(self):
        return (self.member.x2 + self.member.x1) / 2.

    @property
    def y(self):
        return (self.member.y2 + self.member.y1) / 2.


class DataEditor(BoxEditor):
    def setTemplate(self, template):
        self.member = template.data
        self.outline = template.box1
        super(DataEditor, self).setTemplate(template)

    def setBoxWidth(self, val):
        if not self.template:
            return
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
        self.boxEdited.emit()

    def setBoxHeight(self, val):
        if not self.template:
            return
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
        self.boxEdited.emit()

    def move(self, x, y):
        xdiff = x - self.x
        ydiff = y - self.y

        ytic_len = self.template.ytic2.x2 - self.template.ytic2.x1
        ymintic_len = self.template.ymintic2.x2 - self.template.ymintic2.x1
        xbuffer = max(ytic_len, ymintic_len)

        xtic_len = self.template.ytic2.x2 - self.template.ytic2.x1
        xmintic_len = self.template.ymintic2.x2 - self.template.ymintic2.x1
        # Prevent tics from going offscreen
        ybuffer = max(xtic_len, xmintic_len)

        xlabel1_offset = self.member.y1 - self.template.xlabel1.y
        xlabel2_offset = self.member.y2 - self.template.xlabel2.y
        ylabel1_offset = self.member.x1 - self.template.ylabel1.x
        ylabel2_offset = self.member.x2 - self.template.ylabel2.x

        self.member.x1 = min(1 - xbuffer, max(xbuffer, self.member.x1 + xdiff))
        self.member.x2 = min(1 - xbuffer, max(xbuffer, self.member.x2 + xdiff))
        block = self.width_slider.blockSignals(True)
        self.width_slider.setValue(int(100 * abs(self.member.x2 - self.member.x1)))
        self.width_slider.blockSignals(block)
        self.member.y1 = min(1 - ybuffer, max(ybuffer, self.member.y1 + ydiff))
        self.member.y2 = min(1 - ybuffer, max(ybuffer, self.member.y2 + ydiff))
        block = self.height_slider.blockSignals(True)
        self.height_slider.setValue(int(100 * abs(self.member.y2 - self.member.y1)))
        self.height_slider.blockSignals(block)

        self.template.xtic2.y1 = self.member.y2
        self.template.xtic2.y2 = self.member.y2 + xtic_len
        self.template.xtic1.y1 = self.member.y1
        self.template.xtic1.y2 = self.member.y1 - xtic_len

        self.template.ytic2.x1 = self.member.x2
        self.template.ytic2.x2 = self.member.x2 + ytic_len
        self.template.ytic1.x1 = self.member.x1
        self.template.ytic1.x2 = self.member.x1 - ytic_len

        self.template.ymintic2.x1 = self.member.x2
        self.template.ymintic2.x2 = self.member.x2 + ymintic_len
        self.template.ymintic1.x1 = self.member.x1
        self.template.ymintic1.x2 = self.member.x1 - ymintic_len

        self.template.xmintic2.y1 = self.member.y2
        self.template.xmintic2.y2 = self.member.y2 + xmintic_len
        self.template.xmintic1.y1 = self.member.y1
        self.template.xmintic1.y2 = self.member.y1 - xmintic_len

        self.template.xlabel1.y = self.member.y1 - xlabel1_offset
        self.template.xlabel2.y = self.member.y2 - xlabel2_offset
        self.template.ylabel1.x = self.member.x1 - ylabel1_offset
        self.template.ylabel2.x = self.member.x2 - ylabel2_offset

        self.outline.x1 = self.member.x1
        self.outline.x2 = self.member.x2
        self.outline.y1 = self.member.y1
        self.outline.y2 = self.member.y2

        self.boxEdited.emit()


class LegendEditor(BoxEditor):
    def setTemplate(self, template):
        self.member = template.legend
        self.outline = template.legend
        super(LegendEditor, self).setTemplate(template)

    def move(self, x, y):
        xdiff = x - self.x
        ydiff = y - self.y

        self.member.x1 = min(1, max(0, self.member.x1 + xdiff))
        self.member.x2 = min(1, max(0, self.member.x2 + xdiff))
        self.member.y1 = min(1, max(0, self.member.y1 + ydiff))
        self.member.y2 = min(1, max(0, self.member.y2 + ydiff))
        self.width_slider.setValue(int(100 * abs(self.member.x2 - self.member.x1)))
        self.height_slider.setValue(int(100 * abs(self.member.y2 - self.member.y1)))

        self.boxEdited.emit()
