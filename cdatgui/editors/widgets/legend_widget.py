import pdb
# from cdatgui.editors.widgets.dict_editor import DictEditorWidget
from PySide import QtCore, QtGui
from cdatgui.editors.model import legend
from cdatgui.editors.preview.legend_preview import LegendPreviewWidget
from cdatgui.bases.window_widget import BaseOkWindowWidget
from cdatgui.editors.colormap import QColormapEditor


class LegendEditorWidget(BaseOkWindowWidget):
    def __init__(self, parent=None):
        super(LegendEditorWidget, self).__init__()

        # Create Labels
        colormap_label = QtGui.QLabel("Colormap:")
        start_color_label = QtGui.QLabel("Start Color:")
        end_color_label = QtGui.QLabel("End Color:")
        extend_left_label = QtGui.QLabel("Extend Left")
        extend_right_label = QtGui.QLabel("Extend Right")
        custom_fill_label = QtGui.QLabel("Custom Fill")
        labels_label = QtGui.QLabel("Labels:")
        auto_label = QtGui.QLabel("Auto")
        manual_label = QtGui.QLabel("Manual")
        none_label = QtGui.QLabel("None")

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
        start_color_button = QtGui.QPushButton()
        self.start_colormap_editor = QColormapEditor("color")
        self.start_colormap_editor.choseColorIndex.connect(self.updateStartColorFromEditor)
        start_color_button.clicked.connect(self.start_colormap_editor.show)

        # Create start colormap editor button
        end_color_button = QtGui.QPushButton()
        self.end_colormap_editor = QColormapEditor("color")
        self.end_colormap_editor.choseColorIndex.connect(self.updateEndColorFromEditor)
        end_color_button.clicked.connect(self.end_colormap_editor.show)

        # Create start color spinbox
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
            if text == "Solid":
                button.setChecked(True)
            self.fill_button_group.addButton(button)
            fill_style_layout.addWidget(button)
        self.fill_button_group.buttonClicked.connect(self.changeFillStyle)
        fill_style_layout.insertWidget(0, QtGui.QLabel("Fill Style"))

        self.custom_vertical_layout.addLayout(fill_style_layout)

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
        start_color_layout.addWidget(start_color_button)

        end_color_layout.addWidget(end_color_label)
        end_color_layout.addWidget(self.end_color_spin)
        end_color_layout.addWidget(end_color_button)

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

    def setObject(self, legend):
        self.object = legend
        cur_color_1 = legend.color_1
        cur_color_2 = legend.color_2
        print cur_color_1, cur_color_2

        self.preview.setLegendObject(legend)
        self.preview.update()

    def updateColormap(self, cur_item):
        print cur_item
        self.object.colormap = cur_item
        self.preview.update()

    def updateStartColor(self, value):
        self.object.color_1 = value
        self.object._gm.list()
        self.preview.update()

    def updateEndColor(self, value):
        self.object.color_2 = value
        self.object._gm.list()
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
            # create layout for custom fill

            scroll_area = QtGui.QScrollArea()
            rows_widget = QtGui.QWidget()
            rows_layout = QtGui.QVBoxLayout()
            for index, label in enumerate(self.object.level_names):
                level_layout = QtGui.QHBoxLayout()
                level_layout.addWidget(QtGui.QLabel("Level %s" % str(index+1)))

                color_button = QtGui.QPushButton()
                l_color = self.object.level_color(index)
                r, g, b, a = self.object.rgba_from_index(l_color)
                style_string = "background-color: rgba(%d, %d, %d, %d);" % (r, g, b, a)
                color_button.setStyleSheet(style_string)
                level_layout.addWidget(color_button)
                rows_layout.addLayout(level_layout)


            rows_widget.setLayout(rows_layout)
            scroll_area.setWidget(rows_widget)
            self.custom_vertical_layout.addWidget(scroll_area)
        else:
            self.custom_fill_icon.setArrowType(QtCore.Qt.RightArrow)

        self.preview.update()

    def changeFillStyle(self, button):
        if button.text() == "Solid":
            pass
        elif button.text() == "Hatch":
            pass
        elif button.text() == "Pattern":
            pass

if __name__ == "__main__":
    from cdatgui.utils import pattern_thumbnail
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
