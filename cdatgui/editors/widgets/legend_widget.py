from types import FunctionType

from cdatgui.editors.model.legend import VCSLegend
from cdatgui.editors.widgets.dict_editor import DictEditorWidget
from PySide import QtCore, QtGui
from cdatgui.editors.model import legend
from cdatgui.editors.preview.legend_preview import LegendPreviewWidget
from cdatgui.bases.window_widget import BaseOkWindowWidget
from cdatgui.editors.colormap import QColormapEditor
from cdatgui.utils import pattern_thumbnail
from cdatgui.bases.dynamic_grid_layout import DynamicGridLayout
from functools import partial
import vcs


class ForceResizeScrollArea(QtGui.QScrollArea):
    """Forces a resize of the child widget. Needed for proper resizing of the DynamicGridLayout"""

    def resizeEvent(self, ev):
        super(ForceResizeScrollArea, self).resizeEvent(ev)
        self.widget().setGeometry(0, 0, self.width(), self.height())


class CustomFillWidget(QtGui.QWidget):
    colorChanged = QtCore.Signal(int, int)
    opacityChanged = QtCore.Signal(int, int)
    buttonColorChanged = QtCore.Signal(QtGui.QPushButton, int)
    patternChanged = QtCore.Signal(int, int)
    attributeChanged = QtCore.Signal()
    colormapChanged = QtCore.Signal(str)
    createColormapRequest = QtCore.Signal(FunctionType)

    def __init__(self, index, label, parent=None):
        super(CustomFillWidget, self).__init__()

        # Variables
        self.index = index
        self.label = label
        self.color = None
        self.pattern = 1

        # Label
        level_layout = QtGui.QHBoxLayout()
        level_layout.addWidget(QtGui.QLabel(label))

        # Color button
        self.color_button = QtGui.QPushButton()

        self.color_button.setFixedSize(100, 40)
        self.color_button.clicked.connect(lambda: self.createColormapRequest.emit(self.changeColor))
        level_layout.addWidget(self.color_button)

        # Set pattern for combo boxes
        self.pattern_combo = QtGui.QComboBox()
        self.pattern_combo.setItemDelegate(PatternComboDelegate())
        self.pattern_combo.addItem(QtGui.QIcon(QtGui.QPixmap(100, 100).fill(QtGui.QColor(200, 200, 200, 255))),
                                   "No Pattern")
        for i in range(1, 21):
            self.pattern_combo.addItem(pattern_thumbnail(i), "Pattern %d" % i)
        self.pattern_combo.setCurrentIndex(1)
        self.pattern_combo.setIconSize(QtCore.QSize(40, 40))

        # create alpha slider
        alpha_label = QtGui.QLabel("Alpha:")
        self.alpha_slide = QtGui.QSlider()
        self.alpha_slide.setRange(0, 100)
        self.alpha_slide.setValue(100)
        self.alpha_slide.setOrientation(QtCore.Qt.Horizontal)

        alpha_row = QtGui.QHBoxLayout()
        alpha_row.addWidget(alpha_label)
        alpha_row.addWidget(self.alpha_slide)

        pattern_layout = QtGui.QVBoxLayout()
        pattern_layout.addWidget(self.pattern_combo)
        pattern_layout.addLayout(alpha_row)

        pattern_widget = QtGui.QWidget()
        pattern_widget.setLayout(pattern_layout)

        # set up signals
        self.alpha_slide.valueChanged.connect(self.changeOpacity)
        self.pattern_combo.currentIndexChanged.connect(self.changePattern)

        level_layout.addWidget(pattern_widget)

        level_layout.insertStretch(1, 2)
        level_layout.insertStretch(3, 2)

        self.setLayout(level_layout)

    def setColor(self, color):
        """initialization of button color. Should not call update preview"""
        self.color = color
        self.buttonColorChanged.emit(self.color_button, color)

    def changeOpacity(self, value):
        if value == 0:
            self.pattern_combo.setCurrentIndex(0)
        else:
            if self.pattern_combo.currentIndex() == 0:
                self.pattern_combo.setCurrentIndex(self.pattern)
        self.opacityChanged.emit(self.index, value)
        self.attributeChanged.emit()

    def changeColor(self, color_index):
        self.buttonColorChanged.emit(self.color_button, color_index)
        self.colorChanged.emit(self.index, color_index)
        self.attributeChanged.emit()

    def changePattern(self, selected_index):
        if selected_index == 0:
            self.alpha_slide.setValue(0)
        else:
            self.pattern = selected_index
            self.patternChanged.emit(self.index, selected_index)
            self.attributeChanged.emit()


class PatternComboDelegate(QtGui.QAbstractItemDelegate):
    def __init__(self, parent=None):
        super(PatternComboDelegate, self).__init__()

    def paint(self, painter, option, index):
        """Customizes the view of the combobox for selecting a level pattern"""
        if index.row() == 0:
            flags = 0
            flags |= QtCore.Qt.AlignCenter
            painter.drawText(0, 0, 120, 40, flags, "No Pattern")
        else:
            pattern = pattern_thumbnail(index.row())
            pix = pattern.pixmap(200, 40)
            painter.drawPixmap(0, 40 * index.row(), 200, 40, pix)
            painter.drawRect(0, 40 * index.row(), 200, 40)

        if option.state & QtGui.QStyle.State_MouseOver:
            color = QtGui.QColor(63, 193, 219, 128)
            brush = QtGui.QBrush(color)
            painter.fillRect(option.rect, brush)

    def sizeHint(self, option, index):
        s = QtCore.QSize(200, 40)
        return s


class StartEndSpin(QtGui.QSpinBox):
    validInput = QtCore.Signal()
    invalidInput = QtCore.Signal()

    def __init__(self, parent=None):
        super(StartEndSpin, self).__init__()
        self.min = 0
        self.max = 255

    def isValid(self, valid):
        if valid:
            self.setStyleSheet("color :rgb(0,0,0)")
        else:
            self.setStyleSheet("color :rgb(255,0,0)")

    def validate(self, input, pos):
        if input == "":
            return QtGui.QValidator.Intermediate
        try:
            input = int(input)
        except:
            return QtGui.QValidator.Invalid

        if self.min < input < self.max:
            self.validInput.emit()
            self.isValid(True)
            return QtGui.QValidator.Acceptable

        self.invalidInput.emit()
        self.isValid(False)
        return QtGui.QValidator.Intermediate


class LegendEditorWidget(BaseOkWindowWidget):
    def __init__(self, parent=None):
        super(LegendEditorWidget, self).__init__()

        # Variables
        self.level_count = None
        self.cur_button = None
        self.cur_index = None
        self.colormap_editor = None
        self.gm = None
        self.orig_gm = None

        # Create Labels
        colormap_label = QtGui.QLabel("Colormap:")
        start_color_label = QtGui.QLabel("Start Color:")
        end_color_label = QtGui.QLabel("End Color:")
        extend_left_label = QtGui.QLabel("Extend Left")
        extend_right_label = QtGui.QLabel("Extend Right")
        self.custom_fill_label = QtGui.QLabel("Custom Fill")
        labels_label = QtGui.QLabel("Labels:")

        # Timers
        self.start_timer = QtCore.QTimer()
        self.start_timer.setSingleShot(True)
        self.start_timer.setInterval(1000)
        self.start_timer.timeout.connect(self.updateStartColor)

        self.end_timer = QtCore.QTimer()
        self.end_timer.setSingleShot(True)
        self.end_timer.setInterval(1000)
        self.end_timer.timeout.connect(self.updateEndColor)

        # Create colormap dropdown
        self.colormap_dropdown = QtGui.QComboBox()
        self.colormap_dropdown.addItems(legend.get_colormaps())
        self.colormap_dropdown.setCurrentIndex(11)
        self.colormap_dropdown.currentIndexChanged[str].connect(self.updateColormap)

        # Create start color spinbox
        self.start_color_spin = StartEndSpin(self.start_timer)
        self.start_color_spin.setRange(1, 255)
        self.start_color_spin.validInput.connect(self.start_timer.start)
        self.start_color_spin.invalidInput.connect(self.handleStartColorInvalidInput)

        # Create start colormap editor button
        self.start_color_button = QtGui.QPushButton()
        self.start_color_button.clicked.connect(partial(self.createColormap, self.start_color_spin))

        # Create end color spinbox
        self.end_color_spin = StartEndSpin(self.end_timer)
        self.end_color_spin.setRange(1, 255)
        self.end_color_spin.validInput.connect(self.end_timer.start)
        self.end_color_spin.invalidInput.connect(self.handleEndColorInvalidInput)

        # Create end colormap editor button
        self.end_color_button = QtGui.QPushButton()
        self.end_color_button.clicked.connect(partial(self.createColormap, self.end_color_spin))

        # Create extend check boxes
        self.extend_left_check = QtGui.QCheckBox()
        self.extend_left_check.stateChanged.connect(self.updateExtendLeft)
        self.extend_right_check = QtGui.QCheckBox()
        self.extend_right_check.stateChanged.connect(self.updateExtendRight)

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
        self.start_color_widget = QtGui.QWidget()
        self.start_color_widget.setLayout(start_color_layout)

        end_color_layout.addWidget(end_color_label)
        end_color_layout.addWidget(self.end_color_spin)
        end_color_layout.addWidget(self.end_color_button)
        self.end_color_widget = QtGui.QWidget()
        self.end_color_widget.setLayout(end_color_layout)

        extend_layout.addWidget(self.extend_left_check)
        extend_layout.addWidget(extend_left_label)
        extend_layout.addWidget(self.extend_right_check)
        extend_layout.addWidget(extend_right_label)
        extend_layout.insertStretch(2, 1)

        custom_fill_layout.addWidget(self.custom_fill_icon)
        custom_fill_layout.addWidget(self.custom_fill_label)

        # Add preview
        self.setPreview(LegendPreviewWidget())
        self.preview.setMaximumHeight(300)
        self.preview.setMinimumHeight(200)

        # Insert layouts
        self.vertical_layout.insertLayout(1, colormap_layout)
        self.vertical_layout.insertWidget(2, self.start_color_widget)
        self.vertical_layout.insertWidget(3, self.end_color_widget)
        self.vertical_layout.insertLayout(4, extend_layout)
        self.vertical_layout.insertLayout(5, custom_fill_layout)
        self.vertical_layout.insertLayout(6, labels_layout)

    def createAndSetObject(self, gm, var):
        self.orig_gm = gm
        self.gm = vcs.creategraphicsmethod(vcs.graphicsmethodtype(gm), gm.name)
        self.object = VCSLegend(self.gm, var)

        try:
            self.start_color_spin.setValue(self.object.color_1)
            self.updateButtonColor(self.start_color_button, self.object.color_1)
            self.start_color_button.setFixedSize(100, 25)
        except TypeError:
            self.start_color_widget.setEnabled(False)
            self.start_color_widget.hide()

        try:
            self.end_color_spin.setValue(self.object.color_2)
            self.updateButtonColor(self.end_color_button, self.object.color_2)
            self.end_color_button.setFixedSize(100, 25)
        except TypeError:
            self.end_color_widget.setEnabled(False)
            self.end_color_widget.hide()

        # disable the extend left and right if the gm does not have any - might not actually be needed
        if self.object.ext_left is not None:
            self.extend_left_check.setChecked(self.object.ext_left)
        else:
            self.extend_left_check.setEnabled(False)
            self.extend_left_check.hide()

        if self.object.ext_right is not None:
            self.extend_right_check.setChecked(self.object.ext_right)
        else:
            self.extend_right_check.setEnabled(False)
            self.extend_right_check.hide()

        # disable the custom fill option if the fill style is not custom
        if vcs.isboxfill(self.object._gm):
            if self.object._gm.boxfill_type == 'custom':
                self.enableCustom(self.object._gm.fillareastyle != 'solid')
            else:
                self.disableCustom()

        elif self.object.fill_style:
            self.enableCustom(self.object.fill_style != 'solid')
        else:
            self.disableCustom()

        # select correct colormap index
        if gm.colormap is not None:
            self.colormap_dropdown.setCurrentIndex(self.colormap_dropdown.findText(gm.colormap))

        self.preview.setLegendObject(self.object)
        self.preview.update()

    def updateColormap(self, cur_item, recreate=True):
        if self.object.colormap.name == cur_item:
            return

        self.object.colormap = cur_item
        self.colormap_dropdown.setCurrentIndex(self.colormap_dropdown.findText(cur_item))
        self.preview.update()

        self.level_count = len(self.object.levels)

        self.updateStartColor(recreate=False)
        self.updateEndColor(recreate=False)
        if recreate:
            self.updateCustomFillBox()

    def updateStartColor(self, value=-1, recreate=True):
        if value == -1:
            value = self.start_color_spin.value()
        else:
            self.start_color_spin.setValue(value)

        if self.colormap_editor:
            self.colormap_editor.close()

        self.end_color_spin.min = value
        self.object.color_1 = value
        self.updateButtonColor(self.start_color_button, value)
        self.preview.update()

        if self.custom_fill_icon.arrowType() == QtCore.Qt.DownArrow and recreate:
            self.updateCustomFillBox()

    def updateEndColor(self, value=-1, recreate=True):
        if value == -1:
            value = self.end_color_spin.value()
        else:
            self.end_color_spin.setValue(value)

        if self.colormap_editor:
            self.colormap_editor.close()

        self.start_color_spin.max = value
        self.object.color_2 = value
        self.updateButtonColor(self.end_color_button, value)
        self.preview.update()

        if self.custom_fill_icon.arrowType() == QtCore.Qt.DownArrow and recreate:
            self.updateCustomFillBox()

    def updateExtendLeft(self, state):
        self.object.ext_left = state == QtCore.Qt.Checked
        self.preview.update()
        self.updateCustomFillBox()

    def updateExtendRight(self, state):
        self.object.ext_right = state == QtCore.Qt.Checked
        self.preview.update()
        self.updateCustomFillBox()

    def updateArrowType(self):
        if self.custom_fill_icon.arrowType() == QtCore.Qt.RightArrow:
            self.custom_fill_icon.setArrowType(QtCore.Qt.DownArrow)
            self.fill_style_widget.setVisible(True)
            self.vertical_layout.insertLayout(6, self.custom_vertical_layout)
            self.custom_vertical_layout.addWidget(self.createCustomFillBox())
            self.initateFillStyle()
        else:
            self.object.fill_style = "Solid"
            self.fill_style_widget.setVisible(False)
            self.deleteCustomFillBox()
            self.custom_fill_icon.setArrowType(QtCore.Qt.RightArrow)

        self.preview.update()

    def initateFillStyle(self):
        """Used when creating custom fill to initalize fill style to Solid"""
        for button in self.fill_button_group.buttons():
            if button.text() == self.object.fill_style.capitalize():
                button.click()

    def updateCustomFillBox(self):
        if self.custom_fill_icon.arrowType() == QtCore.Qt.DownArrow:
            self.deleteCustomFillBox()
            self.custom_vertical_layout.addWidget(self.createCustomFillBox())
            self.vertical_layout.insertLayout(6, self.custom_vertical_layout)
            # self.initateFillStyle(self.fill_button_group.checkedButton())
            self.initateFillStyle()

    def createCustomFillBox(self):
        # create layout for custom fill
        scroll_area = ForceResizeScrollArea()
        grid_layout = DynamicGridLayout(400)
        dynamic_widget = QtGui.QWidget()
        dynamic_widget.setLayout(grid_layout)
        scroll_area.setWidgetResizable(True)
        level_names = self.object.level_names
        grid_widgets = []

        # populate rows
        for index, label in enumerate(level_names):
            color = self.object.level_color(index)
            item = CustomFillWidget(index, label, color)
            item.colorChanged.connect(self.object.set_level_color)
            item.opacityChanged.connect(self.object.set_level_opacity)
            item.buttonColorChanged.connect(self.updateButtonColor)
            item.patternChanged.connect(self.object.set_level_pattern)
            item.colormapChanged.connect(self.updateButtonColor)
            item.createColormapRequest.connect(self.createColormap)
            item.setColor(color)
            item.changeOpacity(100)
            item.attributeChanged.connect(self.preview.update)
            grid_widgets.append(item)

        # adding widgets(plural) only calls build grid once instead of once for each widget
        grid_layout.setColumnWidth(int(grid_widgets[-1].minimumSizeHint().width()))
        grid_layout.addNewWidgets(grid_widgets)
        scroll_area.setWidget(dynamic_widget)

        return scroll_area

    def deleteCustomFillBox(self):
        self.vertical_layout.takeAt(6)
        scroll = self.custom_vertical_layout.takeAt(1).widget()
        scroll.deleteLater()

    def changeFillStyle(self, button):
        old_fill_style = self.object.fill_style
        scroll = self.custom_vertical_layout.itemAt(1).widget()
        w = scroll.widget()
        for widget in w.layout().getWidgets():
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
        self.object.fill_style = button.text()
        self.preview.update()

    def createColormap(self, obj):
        self.colormap_editor = QColormapEditor(mode="color")
        items = [self.colormap_editor.colormap.itemText(i) for i in range(self.colormap_editor.colormap.count())]
        self.colormap_editor.colormap.setCurrentIndex(items.index(self.colormap_dropdown.currentText()))
        self.colormap_editor.choseColormap.connect(partial(self.updateColormap, recreate=False))
        self.colormap_editor.choseColorIndex.connect(partial(self.performActionAndClose, obj))
        self.colormap_editor.colormapCreated.connect(self.colormap_dropdown.addItem)
        self.colormap_editor.show()
        if self.start_timer.isActive():
            self.start_timer.stop()
        if self.end_timer.isActive():
            self.end_timer.stop()

    def performActionAndClose(self, obj, color_index=0):
        self.colormap_editor.close()
        if isinstance(obj, QtGui.QSpinBox):
            obj.setValue(color_index)
        else:
            obj(color_index)

    def manageDictEditor(self, button):
        self.object.label_mode = button.text()
        if button.text() == "Manual":
            label_editor = DictEditorWidget()
            labels = self.object.labels
            label_editor.setDict(labels)
            label_editor.dictEdited.connect(self.updateLabels)
            scroll_area = QtGui.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(label_editor)
            self.vertical_layout.insertWidget(self.vertical_layout.count() - 1, scroll_area)
        elif isinstance(self.vertical_layout.itemAt(self.vertical_layout.count() - 2).widget(), QtGui.QScrollArea):
            scroll_area = self.vertical_layout.takeAt(self.vertical_layout.count() - 2).widget()
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

    def handleStartColorInvalidInput(self):
        self.start_timer.stop()
        self.start_color_button.setStyleSheet(
            self.start_color_button.styleSheet() + "border: 1px solid red;")

    def handleEndColorInvalidInput(self):
        self.end_timer.stop()
        self.end_color_button.setStyleSheet(
            self.end_color_button.styleSheet() + "border: 1px solid red;")

    def enableCustom(self, show=False):
        self.custom_fill_icon.setEnabled(True)
        self.custom_fill_icon.show()
        self.custom_fill_label.show()
        if show and self.custom_fill_icon.arrowType() == QtCore.Qt.RightArrow:
            self.updateArrowType()

    def disableCustom(self):
        self.custom_fill_icon.setEnabled(False)
        self.custom_fill_icon.hide()
        self.custom_fill_label.hide()
        
    def accept(self):
        orig_name = self.orig_gm.name
        if orig_name in vcs.elements[vcs.graphicsmethodtype(self.orig_gm)]:
            del vcs.elements[vcs.graphicsmethodtype(self.orig_gm)][orig_name]

        new_gm = vcs.creategraphicsmethod(vcs.graphicsmethodtype(self.orig_gm), self.gm.name, orig_name)
        super(LegendEditorWidget, self).accept()

    def reject(self):
        if self.gm.name in vcs.elements[vcs.graphicsmethodtype(self.orig_gm)]:
            del vcs.elements[vcs.graphicsmethodtype(self.orig_gm)][self.gm.name]
        super(LegendEditorWidget, self).reject()


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
