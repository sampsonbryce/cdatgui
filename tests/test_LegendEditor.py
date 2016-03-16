import pytest, cdms2, vcs
from PySide import QtCore, QtGui
from cdatgui.editors.widgets.legend_widget import LegendEditorWidget
from cdatgui.editors.model import legend


@pytest.fixture
def editors():
    editor = LegendEditorWidget()
    b = vcs.createboxfill()
    v = cdms2.open(vcs.sample_data + "/clt.nc")("clt")
    l = legend.VCSLegend(b, v)
    editor.setObject(l)

    return editor


def test_updateColormap(qtbot, editors):
    editors.updateColormap("rainbow")
    assert editors.object.colormap.getname() == "rainbow"


def test_updateStartAndEndColor(editors):
    editors.start_color_spin.setValue(55)

    # have to call because of timer
    editors.updateStartColor(True, False)
    assert editors.object.color_1 == 55

    editors.end_color_spin.setValue(176)

    # have to call because of timer
    editors.updateEndColor(True, False)
    assert editors.object.color_2 == 176


def test_extends(editors):
    editors.updateExtendLeft(QtCore.Qt.Checked)
    assert editors.object.ext_left

    editors.updateExtendRight(QtCore.Qt.Checked)
    assert editors.object.ext_right

    editors.updateExtendLeft(QtCore.Qt.Unchecked)
    assert not editors.object.ext_left

    editors.updateExtendRight(QtCore.Qt.Unchecked)
    assert not editors.object.ext_right


def test_customFillInsertAndDelete(editors):
    assert editors.vertical_layout.count() == 8
    assert editors.custom_vertical_layout.count() == 1

    editors.custom_fill_icon.setArrowType(QtCore.Qt.RightArrow)
    editors.updateArrowType()
    assert editors.vertical_layout.count() == 9
    assert editors.custom_vertical_layout.count() == 2

    editors.custom_fill_icon.setArrowType(QtCore.Qt.DownArrow)
    editors.updateArrowType()
    assert editors.vertical_layout.count() == 8
    assert editors.custom_vertical_layout.count() == 1


def test_changeFillStyle(editors):
    editors.custom_fill_icon.setArrowType(QtCore.Qt.RightArrow)
    editors.updateArrowType()
    assert editors.vertical_layout.count() == 9
    assert editors.custom_vertical_layout.count() == 2

    solid_button = editors.fill_style_widget.layout().itemAt(1).widget()
    editors.changeFillStyle(solid_button)
    assert editors.object.fill_style == "solid"

    hatch_button = editors.fill_style_widget.layout().itemAt(2).widget()
    editors.changeFillStyle(hatch_button)
    assert editors.object.fill_style == "hatch"

    pattern_button = editors.fill_style_widget.layout().itemAt(3).widget()
    editors.changeFillStyle(pattern_button)
    assert editors.object.fill_style == "pattern"


def test_createColormap(editors):
    editors.createColormap(editors.start_color_button, 0)
    editors.colormap_editor.choseColorIndex.emit(60)
    assert editors.object.color_1 == 60
    assert editors.start_color_spin.value() == 60

    editors.createColormap(editors.end_color_button, 0)
    editors.colormap_editor.choseColorIndex.emit(150)
    assert editors.object.color_2 == 150
    assert editors.end_color_spin.value() == 150

    # print editors.custom_vertical_layout.itemAt(1).widget().takeWidget().layout().itemAt(0).itemAt(2).widget()
    # editors.createColormap(editors.custom_vertical_layout.itemAt(1).widget().layout().itemAt(0).layout().itemAt(1), 1)
    editors.createColormap(QtGui.QPushButton(), 1)
    editors.colormap_editor.choseColorIndex.emit(160)

    assert editors.object._gm.fillareacolors[1] == 160


def test_createPatternWidget(editors):
    editors.createPatternWidget(QtGui.QPushButton(), 1)
    editors.pattern_selector.layout().itemAt(4).widget().clicked.emit()

    assert editors.object._gm.fillareaindices[1] == 5


def test_dictEditor(editors):
    editors.manageDictEditor(QtGui.QPushButton("Manual"))
    assert editors.vertical_layout.count() == 9

    dictWidget = editors.vertical_layout.itemAt(editors.vertical_layout.count()-2).widget().takeWidget()
    dictWidget.emitSignal()
    editors.vertical_layout.itemAt(editors.vertical_layout.count()-2).widget().setWidget(dictWidget)

    editors.manageDictEditor(QtGui.QPushButton())
    assert editors.vertical_layout.count() == 8

def test_updateCustomOnColormapChange(editors):
    editors.updateArrowType()

    editors.updateColormap("rainbow")

    assert editors.vertical_layout.count() == 9
