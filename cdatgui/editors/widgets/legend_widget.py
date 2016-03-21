from cdatgui.editors.widgets.dict_editor import DictEditorWidget
from PySide import QtCore, QtGui
from cdatgui.editors.model import legend
from cdatgui.editors.preview.legend_preview import LegendPreviewWidget
from cdatgui.bases.window_widget import BaseOkWindowWidget
from cdatgui.editors.colormap import QColormapEditor
from cdatgui.utils import pattern_thumbnail
from cdatgui.bases.reflow_widget import ReflowWidget
from functools import partial
import timeit


class StartEndSpinBox(QtGui.QSpinBox):
    def __init__(self, func, parent=None):
        super(StartEndSpinBox, self).__init__()
        self.parent = parent
        self.function = func

    def validate(self, value, index):
        if self.parent.object == None:
            return QtGui.QValidator.Acceptable
        try:
            value = int(value)
        except ValueError:
            return QtGui.QValidator.Intermediate
        if self.function == "start":
            if self.parent.object.color_2 > value:
                return QtGui.QValidator.Acceptable
            return QtGui.QValidator.Intermediate
        elif self.function == "end":
            if self.parent.object.color_1 < value:
                return QtGui.QValidator.Acceptable
            return QtGui.QValidator.Intermediate

        raise Exception("Did not crete StartEndSpin with a valid function")
        return QtGui.QValidator.Invalid


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

        # Timers
        self.start_timer = QtCore.QTimer()
        self.start_timer.setSingleShot(True)
        self.start_timer.setInterval(1000)
        self.start_timer.timeout.connect(partial(self.updateStartColor, True, False))

        self.end_timer = QtCore.QTimer()
        self.end_timer.setSingleShot(True)
        self.end_timer.setInterval(1000)
        self.end_timer.timeout.connect(partial(self.updateEndColor, True, False))

        # Create colormap dropdown
        self.colormap_dropdown = QtGui.QComboBox()
        self.colormap_dropdown.addItems(legend.get_colormaps())
        self.colormap_dropdown.setCurrentIndex(11)
        self.colormap_dropdown.currentIndexChanged[str].connect(self.updateColormap)

        # Create start color spinbox
        self.start_color_spin = StartEndSpinBox("start", self)
        self.start_color_spin.setRange(1, 255)
        self.start_color_spin.valueChanged.connect(lambda: self.start_timer.start())

        # Create start colormap editor button
        self.start_color_button = QtGui.QPushButton()
        self.start_color_button.clicked.connect(partial(self.createColormap, self.start_color_button, 0))

        # Create start colormap editor button
        self.end_color_button = QtGui.QPushButton()
        self.end_color_button.clicked.connect(partial(self.createColormap, self.end_color_button, 0))

        # Create end color spinbox
        self.end_color_spin = StartEndSpinBox("end", self)
        self.end_color_spin.setRange(1, 255)
        self.end_color_spin.valueChanged.connect(lambda: self.end_timer.start())

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
        colormap_layout.addWidget(self.colormap_dropdown)

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
        print "setObject"
        self.object = legend

        self.start_color_spin.setValue(self.object.color_1)
        self.updateButtonColor(self.start_color_button, self.object.color_1)
        self.start_color_button.setFixedSize(100, 25)

        self.end_color_spin.setValue(self.object.color_2)
        self.updateButtonColor(self.end_color_button, self.object.color_2)
        self.end_color_button.setFixedSize(100, 25)

        self.preview.setLegendObject(legend)
        print "after setLegendObject"
        self.preview.update()

    def updateColormap(self, cur_item):
        print "updatecolormap"
        print self.object.colormap.name, cur_item
        if self.object.colormap.name == cur_item:
            return
        self.object.colormap = cur_item
        items = [self.colormap_dropdown.itemText(i) for i in range(self.colormap_dropdown.count())]
        self.colormap_dropdown.setCurrentIndex(items.index(cur_item))
        self.preview.update()

        self.level_count = len(self.object.levels)

        self.updateStartColor(False, True)
        self.updateEndColor(False, True)
        self.updateCustomFillBox()

    def updateStartColor(self, update_custom, colormap):
        print "updateStartColor"
        if not colormap:
            value = self.start_color_spin.value()
        else:
            value = self.object.level_color(0)
        if value > self.object.color_2:
            raise ValueError("Start color cannot be higher index than end color")
        self.object.color_1 = value
        self.updateButtonColor(self.start_color_button, value)
        self.preview.update()

        if self.custom_fill_icon.arrowType() == QtCore.Qt.DownArrow and update_custom:
            self.updateCustomFillBox()

    def updateEndColor(self, update_custom, colormap):
        print "updateEndColor"
        if not colormap:
            value = self.end_color_spin.value()
        else:
            value = self.object.level_color(len(self.object.levels)-1)
        if value < self.object.color_1:
            raise ValueError("End color cannot be lower index than start color")
        self.object.color_2 = value
        self.updateButtonColor(self.end_color_button, value)
        self.preview.update()

        if self.custom_fill_icon.arrowType() == QtCore.Qt.DownArrow and update_custom:
            self.updateCustomFillBox()

    def updateExtendLeft(self, state):
        print "updateExtendLeft"
        self.object.ext_left = state == QtCore.Qt.Checked
        self.preview.update()
        self.updateCustomFillBox()

    def updateExtendRight(self, state):
        print "updateExtendRight"
        self.object.ext_right = state == QtCore.Qt.Checked
        self.preview.update()
        self.updateCustomFillBox()

    def updateArrowType(self):
        print "updateArrowType"
        if self.custom_fill_icon.arrowType() == QtCore.Qt.RightArrow:
            self.custom_fill_icon.setArrowType(QtCore.Qt.DownArrow)
            self.fill_style_widget.setVisible(True)
            self.vertical_layout.insertLayout(6, self.custom_vertical_layout)
            self.custom_vertical_layout.addWidget(self.createCustomFillBox())
            self.initateFillStyle(self.fill_button_group.button(-2))
        else:
            self.object.fill_style = "Solid"
            self.fill_style_widget.setVisible(False)
            self.deleteCustomFillBox()
            self.custom_fill_icon.setArrowType(QtCore.Qt.RightArrow)

        self.preview.update()

    def initateFillStyle(self, old_button):
        print "initiateFillStyle"
        # Make current fill style solid
        for button in self.fill_button_group.buttons():
            if button.text() == old_button.text():
                button.click()

    def updateCustomFillBox(self):
        print "updateCustomFillBox"
        if self.custom_fill_icon.arrowType() == QtCore.Qt.DownArrow:
            self.deleteCustomFillBox()
            self.custom_vertical_layout.addWidget(self.createCustomFillBox())
            self.vertical_layout.insertLayout(6, self.custom_vertical_layout)
            self.initateFillStyle(self.fill_button_group.checkedButton())

    def createCustomFillBox(self):
        print "createCustomFillBox"
        # create layout for custom fill
        scroll_area = QtGui.QScrollArea()
        grid_widget = ReflowWidget(300)
        scroll_area.setWidgetResizable(True)
        level_names = self.object.level_names
        for index, label in enumerate(level_names):
            # Label
            level_layout = QtGui.QHBoxLayout()
            level_layout.addWidget(QtGui.QLabel(label))

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

            level_widget = QtGui.QWidget()
            level_widget.setLayout(level_layout)

            grid_widget.addWidget(level_widget)

        scroll_area.setWidget(grid_widget)

        return scroll_area

    def deleteCustomFillBox(self):
        print "deleteCustomFillBox"
        self.vertical_layout.takeAt(6)
        scroll = self.custom_vertical_layout.takeAt(1).widget()
        w = scroll.takeWidget()
        grid = w.layout()
        child = grid.itemAtPosition(0, 0).widget()
        print "CHILD:", child

        for col in range(len(w.counts)):
            for row in range(w.counts[col]):
                child_layout = child.layout()
                print "CHILD_LAYOUT:", child_layout
                if not child_layout:
                    break

                layout_items = child_layout.takeAt(0)
                while layout_items:
                    if isinstance(layout_items, QtGui.QSpacerItem):
                        child_layout.removeItem(layout_items)
                    else:
                        widget = layout_items.widget()
                        widget.deleteLater()
                    layout_items = child_layout.takeAt(0)
                child = grid.itemAtPosition(row, col)

        w.deleteLater()
        grid.deleteLater()
        scroll.deleteLater()

    def changeFillStyle(self, button):
        print "changeFillStyle"
        start_time = timeit.default_timer()
        print start_time
        old_fill_style = self.object.fill_style
        scroll = self.custom_vertical_layout.itemAt(1).widget()
        w = scroll.widget()
        for widget in w.getWidgets():
            row = widget.layout()
            if not row:
                break
            if button.text() == "Solid":
                row.itemAt(2).widget().show()
                row.itemAt(4).widget().hide()

            elif button.text() == "Hatch":
                if old_fill_style == "solid":
                    row.itemAt(4).widget().show()
                else:
                    row.itemAt(2).widget().show()

            elif button.text() == "Pattern":
                row.itemAt(2).widget().hide()
                row.itemAt(4).widget().show()
        print timeit.default_timer() - start_time
        print "OLD STYLE:", old_fill_style
        self.object.fill_style = button.text()
        self.preview.update()

    def createColormap(self, button, index):
        def changeColor(color_index):
            print "changing color"
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
        items = [self.colormap_editor.colormap.itemText(i) for i in range(self.colormap_editor.colormap.count())]
        self.colormap_editor.colormap.setCurrentIndex(items.index(self.colormap_dropdown.currentText()))
        self.colormap_editor.choseColormap.connect(self.updateColormap)
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
            self.vertical_layout.insertWidget(self.vertical_layout.count() - 1, scroll_area)
        elif isinstance(self.vertical_layout.itemAt(self.vertical_layout.count() - 2).widget(), QtGui.QScrollArea):
            scroll_area = self.vertical_layout.takeAt(self.vertical_layout.count() - 2).widget()
            dict_editor = scroll_area.takeWidget()
            dict_editor.clearRows()
            dict_editor.deleteLater()
            scroll_area.deleteLater()

    def updateLabels(self, dict):
        print "updateLabels"
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
