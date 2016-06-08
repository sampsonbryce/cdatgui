from PySide import QtGui, QtCore

from cdatgui.bases.vcs_elements_dialog import VCSElementsDialog
from cdatgui.bases.window_widget import BaseSaveWindowWidget
from cdatgui.editors.preview.axis_preview import AxisPreviewWidget
from cdatgui.editors.widgets.dict_editor import DictEditorWidget
import vcs

from cdatgui.utils import label


class AxisEditorWidget(BaseSaveWindowWidget):
    def __init__(self, axis, parent=None):
        super(AxisEditorWidget, self).__init__()
        self.axis = axis
        self.state = None
        self.setSaveDialog(VCSElementsDialog('line'))

        # create layout so you can set the preview
        self.horizontal_layout = QtGui.QHBoxLayout()

        # create labels
        tickmarks_label = QtGui.QLabel("Tickmarks:")
        show_mini_label = QtGui.QLabel("Show Mini Ticks:")
        mini_per_tick_label = QtGui.QLabel("Mini-Ticks Per Tick:")
        preset_label = QtGui.QLabel("Preset:")

        # create rows
        tickmarks_row = QtGui.QHBoxLayout()
        preset_row = QtGui.QHBoxLayout()
        ticks_row = QtGui.QHBoxLayout()
        mini_ticks_row = QtGui.QHBoxLayout()

        # create widgets
        self.ticks_widget = QtGui.QWidget()
        self.ticks_widget.setLayout(ticks_row)
        self.preset_widget = QtGui.QWidget()
        self.preset_widget.setLayout(preset_row)
        self.dict_widget = DictEditorWidget()
        self.dict_widget.dictEdited.connect(self.updateAxisWithDict)

        # set up scrollable for dict editor
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidget(self.dict_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        # Create radio buttons and group them
        self.tickmark_button_group = QtGui.QButtonGroup()
        tickmarks_row.addWidget(tickmarks_label)

        for name in ["Auto", "Manual"]:
            button = QtGui.QRadioButton(name)
            tickmarks_row.addWidget(button)
            if name == "Auto":
                button.setChecked(True)
            self.tickmark_button_group.addButton(button)

        self.tickmark_button_group.buttonClicked.connect(self.updateTickmark)

        # create preset combo box
        self.preset_box = QtGui.QComboBox()
        self.preset_box.addItem("default")
        self.preset_box.addItems(vcs.listelements("list"))
        self.preset_box.currentIndexChanged[str].connect(self.updatePreset)

        preset_row.addWidget(preset_label)
        preset_row.addWidget(self.preset_box)

        # create show mini ticks check box
        self.show_mini_check_box = QtGui.QCheckBox()
        self.show_mini_check_box.stateChanged.connect(self.updateShowMiniTicks)

        # create mini tick spin box
        self.mini_tick_box = QtGui.QSpinBox()
        self.mini_tick_box.setRange(0, 255)
        self.mini_tick_box.valueChanged.connect(self.updateMiniTicks)

        mini_ticks_row.addWidget(show_mini_label)
        mini_ticks_row.addWidget(self.show_mini_check_box)
        mini_ticks_row.addWidget(mini_per_tick_label)
        mini_ticks_row.addWidget(self.mini_tick_box)

        self.adjuster_layout = QtGui.QVBoxLayout()

        well = QtGui.QFrame()
        well.setFrameShape(QtGui.QFrame.StyledPanel)
        well.setFrameShadow(QtGui.QFrame.Sunken)
        self.well_layout = QtGui.QVBoxLayout()
        well.setLayout(self.well_layout)
        self.well_layout.addWidget(label('Edit Preset:'))
        self.well_layout.addLayout(tickmarks_row)
        self.well_layout.addStretch(0)
        self.well_layout.addLayout(mini_ticks_row)

        self.adjuster_layout.insertWidget(0, self.preset_widget)
        self.adjuster_layout.insertWidget(1, well)

        self.horizontal_layout.addLayout(self.adjuster_layout)
        self.vertical_layout.insertLayout(0, self.horizontal_layout)

        self.setPreview(AxisPreviewWidget())

    def setPreview(self, preview):
        if self.preview:
            raise Exception("Preview already set")

        self.preview = preview
        self.preview.setMinimumWidth(150)
        self.preview.setMaximumWidth(350)

        if self.axis[0] == "y":
            self.horizontal_layout.insertWidget(0, self.preview)
        elif self.axis[0] == "x":
            self.adjuster_layout.insertWidget(0, self.preview)

    def setAxisObject(self, axis_obj):
        self.object = axis_obj

        # initialize combo value
        if isinstance(axis_obj.ticks, str):
            if axis_obj.ticks == '*':
                ticks = 'default'
            else:
                ticks = axis_obj.ticks
            self.preset_box.setCurrentIndex(self.preset_box.findText(ticks))
            self.updatePreset(ticks)

        self.preview.setAxisObject(self.object)
        if self.object.ticks != '*':
            self.show_mini_check_box.setChecked(self.object.show_miniticks)
            self.mini_tick_box.setValue(self.object.minitick_count)

        # set initial mode
        for button in self.tickmark_button_group.buttons():
            if self.object.ticks == '*' and button.text() == 'Manual':
                button.setEnabled(False)

        self.preview.update()
        self.accepted.connect(self.saveTicks)
        self.rejected.connect(self.object.cancel)

    # Update mode essentially
    def updateTickmark(self, button):

        if button.text() == "Auto":
            if self.well_layout.itemAt(2).widget() == self.scroll_area:
                widget = self.well_layout.takeAt(2).widget()
                widget.setVisible(False)

        elif button.text() == "Manual":
            self.well_layout.insertWidget(2, self.scroll_area)
            self.dict_widget.setDict(self.object.ticks_as_dict())
            self.scroll_area.setVisible(True)

        self.object.mode = button.text().lower()
        self.preview.update()

    def updatePreset(self, preset):
        if preset == "default":
            self.object.show_miniticks = False
            self.object.ticks = "*"
            self.save_button.setEnabled(False)
            self.saveas_button.setEnabled(False)
            self.mini_tick_box.setEnabled(False)
            self.show_mini_check_box.setEnabled(False)
            for button in self.tickmark_button_group.buttons():
                if button.text() == 'Manual':
                    button.setEnabled(False)
        else:
            self.object.ticks = preset
            self.save_button.setEnabled(True)
            self.saveas_button.setEnabled(True)
            self.mini_tick_box.setEnabled(True)
            self.show_mini_check_box.setEnabled(True)
            for button in self.tickmark_button_group.buttons():
                if button.text() == 'Manual':
                    button.setEnabled(True)
            if self.dict_widget.isVisible():
                self.dict_widget.setDict(self.object.ticks_as_dict())

        self.preview.update()

    def updateShowMiniTicks(self, state):
        self.object.show_miniticks = (state == QtCore.Qt.Checked)
        self.preview.update()

    def updateMiniTicks(self, mini_count):
        self.object.minitick_count = int(mini_count)
        self.preview.update()

    def updateAxisWithDict(self, dict):
        float_dict = {float(key): value for key, value in dict.items()}
        self.object.ticks = float_dict
        self.preview.update()

    def saveTicks(self, name):
        print "name", name
        if not name:
            name = self.preset_box.currentText()
        self.object.save(name)
