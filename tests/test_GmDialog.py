import pytest, vcs, cdms2, os

from cdatgui.editors.model.legend import VCSLegend
from cdatgui.graphics.dialog import *
from cdatgui.cdat.metadata import FileMetadataWrapper
from cdatgui.editors import boxfill, isoline, cdat1d
from PySide import QtCore, QtGui


@pytest.fixture
def boxfill_dialog():
    s = get_var()
    d = GraphicsMethodDialog(vcs.getboxfill('default'), s, vcs.createtemplate())
    d.createdGM.connect(saveAs)
    return d


@pytest.fixture
def isoline_dialog():
    s = get_var()
    d = GraphicsMethodDialog(vcs.getisoline('default'), s, vcs.createtemplate())
    return d


@pytest.fixture
def oned_dialog():
    s = get_var()
    d = GraphicsMethodDialog(vcs.get1d('default'), s, vcs.createtemplate())
    return d


@pytest.fixture
def save_dialog():
    s = get_var()
    d = GraphicsMethodSaveDialog(vcs.getmeshfill('a_meshfill'), s, vcs.createtemplate())
    return d


@pytest.fixture
def ok_dialog():
    s = get_var()
    d = GraphicsMethodOkDialog(vcs.getboxfill('a_boxfill'), s, vcs.createtemplate())
    return d


def get_var():
    f = cdms2.open(os.path.join(vcs.sample_data, 'clt.nc'))
    f = FileMetadataWrapper(f)
    s = f('clt')
    return s


def saveAs(gm):
    assert gm.name == 'test'


def test_boxfillDialog(qtbot, boxfill_dialog):
    """Test boxfill gm editor as well as basic dialog functionality and GraphicsMethodEditor functionality"""
    editor = boxfill_dialog.editor

    assert isinstance(editor, boxfill.BoxfillEditor)
    assert editor.levels_button.isEnabled() == False

    for button in editor.type_group.buttons():
        if button.text() == 'Custom':
            button.click()
            break

    assert editor.levels_button.isEnabled() == True
    assert editor.gm.boxfill_type == 'custom'

    editor.levels_button.click()
    qtbot.addWidget(editor.level_editor)
    assert editor.level_editor
    editor.level_editor.close()

    for button in editor.type_group.buttons():
        if button.text() == 'Logarithmic':
            button.click()
            break

    assert editor.levels_button.isEnabled() == False
    # save_button = boxfill_dialog.layout().itemAt(1).layout().itemAt(3).widget()
    # assert save_button.isEnabled() == False
    # boxfill_dialog.save(('test', True))

    # test ticks dialogs
    editor.editLeft()
    assert editor.axis_editor
    assert editor.axis_editor.axis == 'y1'

    editor.updated()
    assert editor.axis_editor is None

    editor.editRight()
    assert editor.axis_editor.axis == 'y2'

    editor.updated()
    assert editor.axis_editor is None

    editor.editBottom()
    assert editor.axis_editor.axis == 'x1'

    editor.updated()
    assert editor.axis_editor is None

    editor.editTop()
    qtbot.addWidget(editor.axis_editor)
    assert editor.axis_editor.axis == 'x2'

    editor.updated()

    # testing legend crashes with autolabels error. autolabels not supposed to implemented?
    # editor.editLegend()
    # assert editor.legend_editor
    # assert isinstance(editor.object, VCSLegend)

    # editor.updated()

    editor.editProjection()
    assert editor.projection_editor
    assert editor.projection_editor.cur_projection_name == 'linear'
    editor.projection_editor.close()

    editor.updated()
    assert editor.axis_editor is None
    assert editor.projection_editor is None

    boxfill_dialog.reject()


def test_isolineDialog(qtbot, isoline_dialog):
    editor = isoline_dialog.editor
    assert isinstance(editor, isoline.IsolineEditor)

    assert not editor.text_edit_widget
    assert not editor.line_edit_widget

    assert editor.label_check.isChecked() == False
    assert editor.edit_label_button.isEnabled() == False

    editor.updateLabel(QtCore.Qt.Checked)
    assert editor.gm.label == True
    assert editor.edit_label_button.isEnabled() == True

    editor.editText()
    qtbot.addWidget(editor.text_edit_widget)
    assert editor.text_edit_widget

    editor.editLines()
    qtbot.addWidget(editor.line_edit_widget)
    assert editor.line_edit_widget

    editor.updateLabel(QtCore.Qt.Unchecked)
    assert editor.gm.label == False
    assert editor.edit_label_button.isEnabled() == False


def test_1dDialog(qtbot, oned_dialog):
    # really only testing this because it has a marker button.
    editor = oned_dialog.editor
    assert isinstance(editor, cdat1d.Cdat1dEditor)

    editor.flipGraph(QtCore.Qt.Checked)
    assert editor.gm.flip == True

    editor.editMarker()
    qtbot.addWidget(editor.marker_editor)
    assert editor.marker_editor

    editor.editLine()
    qtbot.addWidget(editor.line_editor)
    assert editor.line_editor

    oned_dialog.reject()
    assert oned_dialog.newgm_name not in vcs.listelements('1d')


def test_saveDialog(qtbot, save_dialog):
    assert save_dialog.origgm_name == 'a_meshfill'
    save_button = save_dialog.layout().itemAt(1).layout().itemAt(3).widget()
    assert save_button.isEnabled() == True
    save_dialog.customName()
    assert isinstance(save_dialog.dialog, VcsElementsDialog)


def test_okDialog(qtbot, ok_dialog):
    assert ok_dialog.origgm_name == 'a_boxfill'
    ok_dialog.accept()
    assert ok_dialog.newgm_name not in vcs.listelements('boxfill')


def test_saveButtonDisabled(qtbot):
    s = get_var()
    d = GraphicsMethodSaveDialog(vcs.getisoline('default'), s, vcs.createtemplate())
    save_button = d.layout().itemAt(1).layout().itemAt(3).widget()
    assert save_button.isEnabled() == False

    # boxfill_dialog.save(('test', True))
