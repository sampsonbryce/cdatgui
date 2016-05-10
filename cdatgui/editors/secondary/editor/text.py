import vcs
from cdatgui.editors.secondary.preview.text import TextStylePreviewWidget
from PySide import QtCore, QtGui
from cdatgui.bases.window_widget import BaseSaveWindowWidget
from cdatgui.vcsmodel import get_textstyles


class TextStyleEditorWidget(BaseSaveWindowWidget):
    saved = QtCore.Signal(str)

    def __init__(self):
        super(TextStyleEditorWidget, self).__init__()
        self.setPreview(TextStylePreviewWidget())
        self.accepted.connect(self.saveNewText)
        self.orig_names = []
        self.newtextcombined_name = None

        # Set up vertical align
        self.va_group = QtGui.QButtonGroup()
        va_layout = QtGui.QHBoxLayout()

        for alignment in ["Top", "Mid", "Bot"]:
            button = QtGui.QPushButton()
            button.setText(alignment)
            button.setCheckable(True)
            va_layout.addWidget(button)
            self.va_group.addButton(button)

        self.va_group.buttonClicked.connect(self.updateButton)

        va_box = QtGui.QGroupBox()
        va_box.setLayout(va_layout)
        va_box.setTitle("Vertical Align")

        # Set up horizontal group
        self.ha_group = QtGui.QButtonGroup()
        ha_layout = QtGui.QHBoxLayout()

        for alignment in ["Left", "Center", "Right"]:
            button = QtGui.QPushButton()
            button.setText(alignment)
            button.setCheckable(True)
            ha_layout.addWidget(button)
            self.ha_group.addButton(button)

        self.ha_group.buttonClicked.connect(self.updateButton)

        ha_box = QtGui.QGroupBox()
        ha_box.setLayout(ha_layout)
        ha_box.setTitle("Horizontal Align")

        # First row
        align_angle_row = QtGui.QHBoxLayout()
        align_angle_row.addWidget(va_box)
        align_angle_row.addWidget(ha_box)
        align_angle_row.insertStretch(2, 1)

        # Create labels
        angle_label = QtGui.QLabel()
        angle_label.setText("Angle:")
        font_label = QtGui.QLabel()
        font_label.setText("Font:")
        size_label = QtGui.QLabel()
        size_label.setText("Size:")

        # angle dial setup
        self.angle_slider = QtGui.QDial()
        self.angle_slider.setRange(90, 450)  # set rotate values so dial orientation matches initial text
        self.angle_slider.setWrapping(True)
        self.angle_slider.setNotchesVisible(True)
        self.angle_slider.valueChanged.connect(self.updateAngle)

        align_angle_row.addWidget(angle_label)
        align_angle_row.addWidget(self.angle_slider)

        # Font combobox
        self.font_box = QtGui.QComboBox()
        for item in vcs.listelements("font"):
            self.font_box.addItem(item)
        self.font_box.currentIndexChanged[str].connect(self.updateFont)

        # size spin box
        self.size_box = QtGui.QSpinBox()
        self.size_box.setRange(1, 128)
        self.size_box.valueChanged.connect(self.updateSize)

        font_size_row = QtGui.QHBoxLayout()
        font_size_row.addWidget(font_label)
        font_size_row.addWidget(self.font_box)
        font_size_row.addWidget(size_label)
        font_size_row.addWidget(self.size_box)
        font_size_row.insertStretch(2, 3)

        # Set up wrap
        self.vertical_layout.insertLayout(1, align_angle_row)
        self.vertical_layout.insertLayout(2, font_size_row)

    def setTextObject(self, text_object):
        self.orig_names = [text_object.name, text_object.Tt_name, text_object.To_name]

        if text_object.Tt_name == 'default' and text_object.To_name == 'default':
            self.save_button.setEnabled(False)

        text_object = vcs.createtextcombined(Tt_source=text_object.Tt_name, To_source=text_object.To_name)
        self.newtextcombined_name = text_object.name

        self.object = text_object
        self.preview.setTextObject(self.object)
        self.setWindowTitle('Edit Style "%s"' % self.object.name.split(':::')[0])

        # set initial values
        cur_valign = self.object.valign
        for button in self.va_group.buttons():
            if cur_valign == 0 and button.text() == "Top":
                button.setChecked(True)
            elif cur_valign == 2 and button.text() == "Mid":
                button.setChecked(True)
            elif cur_valign == 4 and button.text() == "Bot":
                button.setChecked(True)

        cur_halign = self.object.halign
        for button in self.ha_group.buttons():
            if cur_halign == 0 and button.text() == "Left":
                button.setChecked(True)
            elif cur_halign == 1 and button.text() == "Center":
                button.setChecked(True)
            elif cur_halign == 2 and button.text() == "Right":
                button.setChecked(True)

        self.angle_slider.setSliderPosition(self.object.angle)
        self.size_box.setValue(self.object.height)

    def updateButton(self, button):
        if button.text() == "Top":
            self.object.valign = "top"
        elif button.text() == "Mid":
            self.object.valign = "half"
        elif button.text() == "Bot":
            self.object.valign = "bottom"
        elif button.text() == "Left":
            self.object.halign = "left"
        elif button.text() == "Center":
            self.object.halign = "center"
        elif button.text() == "Right":
            self.object.halign = "right"
        self.preview.update()

    def updateAngle(self, angle):
        self.object.angle = angle % 360  # angle cannot be higher than 360
        self.preview.update()

    def updateFont(self, font):
        self.object.font = str(font)
        self.preview.update()

    def updateSize(self, size):
        self.object.height = size
        self.preview.update()

    def saveNewText(self, name):
        name = str(name)
        tt_name, to_name = self.newtextcombined_name.split(':::')

        if name != self.newtextcombined_name:
            to = vcs.elements['textorientation'][to_name]
            tt = vcs.elements['texttable'][tt_name]

            # deleting if already exists. This will only happen if they want to overwrite
            if name in vcs.elements['texttable']:
                del vcs.elements['texttable'][name]
            if name in vcs.elements['textorientation']:
                del vcs.elements['textorientation'][name]

            # inserting new object
            new_tt = vcs.createtexttable(name, source=tt)
            new_to = vcs.createtextorientation(name, source=to)
            vcs.elements['textorientation'][name] = new_to
            vcs.elements['texttable'][name] = new_tt

            # removing old object from key
            vcs.elements['textorientation'].pop(to_name)
            vcs.elements['texttable'].pop(tt_name)

            tc = vcs.createtextcombined()
            tc.Tt = new_tt
            tc.To = new_to

            # inserting into model
            get_textstyles().updated(name)

            # adding to list
            self.saved.emit(name)

        else:
            # recover original info
            old_tt = vcs.elements['texttable'][self.orig_names[1]]
            old_to = vcs.elements['textorientation'][self.orig_names[2]]

            # get new info
            new_tt = vcs.elements['texttable'][tt_name]
            new_to = vcs.elements['textorientation'][to_name]

            # delete old tt and to
            old_tt_name = old_tt.name
            old_to_name = old_to.name

            del vcs.elements['texttable'][self.orig_names[1]]
            del vcs.elements['textorientation'][self.orig_names[2]]

            # create new tt and to objects with old name and new attributes
            brand_new_tt = vcs.createtexttable(old_tt_name, source=new_tt)
            brand_new_to = vcs.createtextorientation(old_to_name, source=new_to)

            tc = vcs.createtextcombined()
            tc.Tt = brand_new_tt
            tc.To = brand_new_to
            vcs.elements['textcombined'][self.orig_names[0]] = tc

            # inserting into model
            get_textstyles().updated(old_tt_name)

            # adding to list
            self.saved.emit(old_tt_name)

    def close(self):
        tt_name, to_name = self.newtextcombined_name.split(':::')
        if self.newtextcombined_name in vcs.elements['textcombined']:
            del vcs.elements['textcombined'][self.newtextcombined_name]
            if to_name in vcs.listelements('textorientation'):
                del vcs.elements['textorientation'][to_name]
            if tt_name in vcs.listelements('texttable'):
                del vcs.elements['texttable'][tt_name]
        super(TextStyleEditorWidget, self).close()
