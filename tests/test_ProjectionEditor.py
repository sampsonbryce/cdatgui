import vcs, cdms2, pytest
from PySide import QtCore, QtGui
from cdatgui.editors.projection_editor import ProjectionEditor


@pytest.fixture
def editor():
    edit = ProjectionEditor()
    gm = vcs.createboxfill()
    proj_obj = vcs.getprojection('linear')
    edit.setProjectionObject(proj_obj)
    edit.gm = gm
    return edit


def test_changingNameAndType(qtbot, editor):
    orig_ortho = vcs.elements['projection']['orthographic']
    assert editor.vertical_layout.count() == 3
    assert editor.proj_combo.currentText() == 'linear'
    assert editor.type_combo.currentText() == 'linear'

    editor.proj_combo.setCurrentIndex(5)
    assert editor.cur_projection_name == 'orthographic'
    assert editor.type_combo.currentText() == 'orthographic'
    assert len(editor.editors) == 5

    editor.type_combo.setCurrentIndex(editor.type_combo.findText('hotin oblique merc'))
    assert len(editor.editors) == 11
    assert editor.cur_projection_name == 'orthographic'
    assert editor.type_combo.currentText() == 'hotin oblique merc'

    editor.save()

    assert vcs.elements['projection']['orthographic'] != orig_ortho
    assert vcs.elements['projection']['orthographic'].type == 'hotin oblique merc'
    assert 'new' not in vcs.listelements('projection')


def test_savAs(qtbot, editor):
    orig_poly = vcs.elements['projection']['polyconic']
    assert editor.vertical_layout.count() == 3
    assert editor.proj_combo.currentText() == 'linear'
    assert editor.type_combo.currentText() == 'linear'

    editor.proj_combo.setCurrentIndex(7)
    assert editor.cur_projection_name == 'polyconic'
    assert editor.type_combo.currentText() == 'polyconic'
    assert len(editor.editors) == 6

    editor.saveAs()
    qtbot.addWidget(editor.win)
    editor.win.setTextValue('test')
    editor.win.accepted.emit()

    assert vcs.elements['projection']['polyconic'] == orig_poly
    assert 'test' in vcs.listelements('projection')
    assert 'new' not in vcs.listelements('projection')


def test_close(qtbot, editor):
    assert 'new' in vcs.listelements('projection')
    assert editor.cur_projection_name == 'linear'
    assert editor.object.type == 'linear'

    editor.updateCurrentProjection('mollweide')
    assert editor.cur_projection_name == 'mollweide'
    assert editor.object.type == 'mollweide'
    editor.close()

    assert 'new' not in vcs.listelements('projection')
    assert vcs.getprojection('linear').name == 'linear'
    assert vcs.getprojection('linear').type == 'linear'
