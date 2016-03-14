from cdatgui.editors.widgets.dict_editor import DictEditorWidget
from PySide import QtCore, QtGui
from cdatgui.editors.model import legend
from cdatgui.editors.preview.legend_preview import LegendPreviewWidget
from cdatgui.bases.window_widget import BaseOkWindowWidget
from cdatgui.editors.colormap import QColormapEditor
from cdatgui.utils import pattern_thumbnail
from functools import partial


class LegendEditorWidget(BaseOkWindowWidget):
    def __init__(self, parent=None):
        super(LegendEditorWidget, self).__init__()

        # Variables
        self.level_count = None

        # Create Labels
        colormap_label = QtGui.QLabel("Colormap:")
        start_color_label = QtGui.QLabel("Start Color:")
        end_color_label = QtGui.QLabel("End Color:")
        extend_left_label = QtGui.QLabel("Extend Left")
        extend_right_label = QtGui.QLabel("Extend Right")
        custom_fill_label = QtGui.QLabel("Custom Fill")
        labels_label = QtGui.QLabel("Labels:")

        # Create colormap dropdown
        colormap_dropdown = QtGui.QComboBox()
        colormap_dropdown.addItems(legend.get_colormaps())
        colormap_dropdown.setCurrentIndex(11)
        colormap_dropdown.currentIndexChanged[str].connect(self.updateColormap)

        # Create start color spinbox
        self.start_color_spin = QtGui.QSpinBox()
        self.start_color_spin.setRange(1, 255)
        self.start_color_spin.valueChanged.connect(self.updateStartColor)

        # Create start colormap editor button
        self.start_color_button = QtGui.QPushButton()
        self.start_color_button.clicked.connect(partial(self.createColormap, self.start_color_button, 0))

        # Create start colormap editor button
        self.end_color_button = QtGui.QPushButton()
        self.end_color_button.clicked.connect(partial(self.createColormap, self.end_color_button, 0))

        # Create end color spinbox
        self.end_color_spin = QtGui.QSpinBox()
        self.end_color_spin.setRange(1, 255)
        self.end_color_spin.valueChanged.connect(self.updateEndColor)

        # Create extend check boxes
        extend_left_check = QtGui.QCheckBox()
        extend_left_check.stateChanged.connect(self.updateExtendLeft)
        extend_right_check = QtGui.QCheckBox()
        extend_right_check.stateChanged.connect(self.updateExtendRight)

        # Create custom fill icon
        self.custom_fill_icon = QtGui.QToolButton()
        self.custom_fill_icon.setArrowType(QtCore.Qt.RightArrow)
        self.custom_fill_icon.clicked.connect(self.updateArrowType)

        # Create custom fill section
        self.custom_vertical_layout = QtGui.QVBoxLayout()

        fill_style_layout = QtGui.QHBoxLayout()
        self.fill_button_group = QtGui.QButtonGroup()
        for text in ["Solid", "Hatch", "Pattern"]:
            button = QtGui.QRadioButton(text)
            if text == "Hatch":
                button.setChecked(True)

            self.fill_button_group.addButton(button)
            fill_style_layout.addWidget(button)

        self.fill_button_group.buttonClicked.connect(self.changeFillStyle)
        fill_style_layout.insertWidget(0, QtGui.QLabel("Fill Style"))

        self.fill_style_widget = QtGui.QWidget()
        self.fill_style_widget.setLayout(fill_style_layout)

        self.custom_vertical_layout.addWidget(self.fill_style_widget)

        # Create labels section
        labels_layout = QtGui.QHBoxLayout()
        labels_layout.addWidget(labels_label)
        self.labels_button_group = QtGui.QButtonGroup()
        for text in ["Auto", "Manual", "None"]:
            button = QtGui.QRadioButton(text)
            if text == "Auto":
                button.setChecked(True)

            self.labels_button_group.addButton(button)
            labels_layout.addWidget(button)

        self.labels_button_group.buttonClicked.connect(self.manageDictEditor)

        # Create layouts
        colormap_layout = QtGui.QHBoxLayout()
        start_color_layout = QtGui.QHBoxLayout()
        end_color_layout = QtGui.QHBoxLayout()
        extend_layout = QtGui.QHBoxLayout()
        custom_fill_layout = QtGui.QHBoxLayout()

        colormap_layout.addWidget(colormap_label)
        colormap_layout.addWidget(colormap_dropdown)

        start_color_layout.addWidget(start_color_label)
        start_color_layout.addWidget(self.start_color_spin)
        start_color_layout.addWidget(self.start_color_button)

        end_color_layout.addWidget(end_color_label)
        end_color_layout.addWidget(self.end_color_spin)
        end_color_layout.addWidget(self.end_color_button)

        extend_layout.addWidget(extend_left_check)
        extend_layout.addWidget(extend_left_label)
        extend_layout.addWidget(extend_right_check)
        extend_layout.addWidget(extend_right_label)
        extend_layout.insertStretch(2, 1)

        custom_fill_layout.addWidget(self.custom_fill_icon)
        custom_fill_layout.addWidget(custom_fill_label)

        # Add preview
        self.setPreview(LegendPreviewWidget())
        self.preview.setMaximumHeight(300)
        self.preview.setMinimumHeight(200)

        # Insert layouts
        self.vertical_layout.insertLayout(1, colormap_layout)
        self.vertical_layout.insertLayout(2, start_color_layout)
        self.vertical_layout.insertLayout(3, end_color_layout)
        self.vertical_layout.insertLayout(4, extend_layout)
        self.vertical_layout.insertLayout(5, custom_fill_layout)
        self.vertical_layout.insertLayout(6, labels_layout)

    def setObject(self, legend):
        self.object = legend

        self.start_color_spin.setValue(self.object.color_1)
        self.updateButtonColor(self.start_color_button, self.object.color_1)
        self.start_color_button.setFixedSize(100, 25)

        self.end_color_spin.setValue(self.object.color_2)
        self.updateButtonColor(self.end_color_button, self.object.color_2)
        self.end_color_button.setFixedSize(100, 25)

        self.preview.setLegendObject(legend)
        self.preview.update()

    def updateColormap(self, cur_item):
        self.object.colormap = cur_item
        self.preview.update()

        self.level_count = len(self.object.levels)

        if self.custom_fill_icon.arrowType() == QtCore.Qt.DownArrow:
            self.deleteCustomFillBox()
            self.custom_vertical_layout.addWidget(self.createCustomFillBox())

        start_color = self.object.level_color(0)
        end_color = self.object.level_color(self.level_count-1)
        self.updateButtonColor(self.start_color_button, start_color)
        self.start_color_spin.setValue(start_color)
        self.updateButtonColor(self.end_color_button, end_color)
        self.end_color_spin.setValue(end_color)

    def updateStartColor(self, value):
        self.object.color_1 = value
        self.updateButtonColor(self.start_color_button, value)
        self.preview.update()

    def updateEndColor(self, value):
        self.object.color_2 = value
        self.updateButtonColor(self.end_color_button, value)
        self.preview.update()

    def updateStartColorFromEditor(self, value):
        self.start_color_spin.setValue(value)
        self.preview.update()

    def updateEndColorFromEditor(self, value):
        self.end_color_spin.setValue(value)
        self.preview.update()

    def updateExtendLeft(self, state):
        self.object.ext_left = state == QtCore.Qt.Checked
        self.preview.update()

    def updateExtendRight(self, state):
        self.object.ext_right = state == QtCore.Qt.Checked
        self.preview.update()

    def updateArrowType(self):
        if self.custom_fill_icon.arrowType() == QtCore.Qt.RightArrow:
            self.custom_fill_icon.setArrowType(QtCore.Qt.DownArrow)
            self.vertical_layout.insertLayout(6, self.custom_vertical_layout)
            self.fill_style_widget.setVisible(True)
            self.custom_vertical_layout.addWidget(self.createCustomFillBox())
        else:
            self.fill_style_widget.setVisible(False)
            self.deleteCustomFillBox()
            self.custom_fill_icon.setArrowType(QtCore.Qt.RightArrow)

        self.preview.update()

    def createCustomFillBox(self):
        # create layout for custom fill
        scroll_area = QtGui.QScrollArea()
        rows_widget = QtGui.QWidget()
        rows_layout = QtGui.QVBoxLayout()
        level_names = self.object.level_names
        for index, label in enumerate(level_names):
            # Label
            level_layout = QtGui.QHBoxLayout()
            level_layout.addWidget(QtGui.QLabel("Level %s" % str(index + 1)))

            # Color button
            color_button = QtGui.QPushButton()
            l_color = self.object.level_color(index)
            self.updateButtonColor(color_button, l_color)

            color_button.setFixedSize(100, 40)

            color_button.clicked.connect(partial(self.createColormap, color_button, index))
            level_layout.addWidget(color_button)

            # Pattern
            pattern = pattern_thumbnail(self.object.level_pattern(index))
            pattern_button = QtGui.QPushButton()
            pattern_button.setIcon(pattern)
            pattern_button.setIconSize(QtCore.QSize(100, 50))
            pattern_button.setFixedSize(100, 50)
            pattern_button.clicked.connect(partial(self.createPatternWidget, pattern_button, index))
            level_layout.addWidget(pattern_button)

            level_layout.insertStretch(1, 2)
            level_layout.insertStretch(3, 2)

            rows_layout.addLayout(level_layout)

        rows_widget.setLayout(rows_layout)
        scroll_area.setWidget(rows_widget)
        return scroll_area

    def deleteCustomFillBox(self):
        scroll = self.custom_vertical_layout.takeAt(1).widget()
        w = scroll.takeWidget()
        l = w.layout()
        child = l.takeAt(0)
        while child:
            sub_child = child.takeAt(0)
            while sub_child:
                if isinstance(sub_child, QtGui.QSpacerItem):
                    child.removeItem(sub_child)
                else:
                    widget = sub_child.widget()
                    widget.deleteLater()
                sub_child = child.takeAt(0)
            child = l.takeAt(0)

        l.deleteLater()
        scroll.deleteLater()

    def changeFillStyle(self, button):
        self.object.fill_style = button.text()
        scroll = self.custom_vertical_layout.itemAt(1).widget()
        w = scroll.takeWidget()
        l = w.layout()
        for row_index in range(l.count()):
            row = l.itemAt(row_index)
            if not row:
                break

            if button.text() == "Solid":
                row.itemAt(2).widget().show()
                row.itemAt(4).widget().hide()

            elif button.text() == "Hatch":
                row.itemAt(2).widget().show()
                row.itemAt(4).widget().show()

            elif button.text() == "Pattern":
                row.itemAt(2).widget().hide()
                row.itemAt(4).widget().show()

        scroll.setWidget(w)
        self.preview.update()

    def createColormap(self, button, index):
        def changeColor(color_index):
            self.updateButtonColor(button, color_index)
            if button != self.start_color_button and button != self.end_color_button:
                self.object.set_level_color(index, color_index)
            elif button == self.start_color_button:
                self.object.color_1 = color_index
                self.start_color_spin.setValue(color_index)
            else:
                self.object.color_2 = color_index
                self.end_color_spin.setValue(color_index)

            self.preview.update()

        self.colormap_editor = QColormapEditor(mode="color")
        self.colormap_editor.choseColorIndex.connect(changeColor)
        self.colormap_editor.show()

    def createPatternWidget(self, button, index):
        def changePattern(selected_index):
            button.setIcon(pattern_thumbnail(selected_index))
            self.object.set_level_pattern(index, selected_index)
            self.pattern_selector.close()
            self.preview.update()

        self.pattern_selector = QtGui.QWidget()
        vertical_layout = QtGui.QVBoxLayout()
        for i in range(1, 21):
            pattern = pattern_thumbnail(i)
            pattern_button = QtGui.QPushButton()
            pattern_button.setIcon(pattern)
            pattern_button.setIconSize(QtCore.QSize(100, 50))
            pattern_button.setFixedSize(100, 50)
            pattern_button.clicked.connect(partial(changePattern, i))
            vertical_layout.addWidget(pattern_button)
        self.pattern_selector.setLayout(vertical_layout)
        self.pattern_selector.show()

    def manageDictEditor(self, button):
        self.object.label_mode = button.text()
        if button.text() == "Manual":
            label_editor = DictEditorWidget()
            labels = self.object.labels
            label_editor.setDict(labels)
            label_editor.dictEdited.connect(self.updateLabels)
            scroll_area = QtGui.QScrollArea()
            scroll_area.setWidget(label_editor)
            self.vertical_layout.insertWidget(self.vertical_layout.count()-1, scroll_area)
        elif isinstance(self.vertical_layout.itemAt(self.vertical_layout.count()-2).widget(), QtGui.QScrollArea):
            scroll_area = self.vertical_layout.itemAt(self.vertical_layout.count()-2).widget()
            scroll_area.takeWidget().deleteLater()
            scroll_area.deleteLater()

    def updateLabels(self, dict):
        try:
            d = {float(key): value for key, value in dict.items()}
            self.object.labels = d
        except ValueError:
            pass

        self.preview.update()

    def updateButtonColor(self, button, color_index):
        r, g, b, a = self.object.rgba_from_index(color_index)
        style_string = "background-color: rgba(%d, %d, %d, %d);" % (r, g, b, a)
        button.setStyleSheet(style_string)

if __name__ == "__main__":
    import cdms2, vcs

    app = QtGui.QApplication([])
    editor = LegendEditorWidget()

    # 1 through 20
    thumb = pattern_thumbnail(1)

    b = vcs.createboxfill()
    v = cdms2.open(vcs.sample_data + "/clt.nc")("clt")
    legend = legend.VCSLegend(b, v)
    editor.setObject(legend)

    editor.show()
    editor.raise_()
    app.exec_()
