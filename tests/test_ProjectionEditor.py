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

    editor.accept()

    assert vcs.elements['projection']['orthographic'] != orig_ortho
    assert vcs.elements['projection']['orthographic'].type == 'hotin oblique merc'
    assert editor.newprojection_name not in vcs.listelements('projection')


def test_saveAs(qtbot, editor):
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
    assert editor.newprojection_name not in vcs.listelements('projection')


def test_close(qtbot, editor):
    assert editor.newprojection_name in vcs.listelements('projection')
    assert editor.cur_projection_name == 'linear'
    assert editor.object.type == 'linear'

    editor.updateCurrentProjection('mollweide')
    assert editor.cur_projection_name == 'mollweide'
    assert editor.object.type == 'mollweide'
    editor.close()

    assert editor.newprojection_name not in vcs.listelements('projection')
    assert vcs.getprojection('linear').name == 'linear'
    assert vcs.getprojection('linear').type == 'linear'


def test_settingAttributes(qtbot, editor):
    old_proj_name = editor.gm.projection
    editor.type_combo.setCurrentIndex(editor.type_combo.findText('robinson'))
    editor.editors[0][0].setText('12')

    editor.accept()

    old_proj = vcs.getprojection(old_proj_name)
    assert old_proj.type == 'robinson'
    assert old_proj.sphere == 12.0

    new_editor = ProjectionEditor()
    qtbot.addWidget(new_editor)
    new_editor.setProjectionObject(old_proj)
    new_editor.gm = editor.gm
    assert new_editor.editors[0][0].text() == '12.0'
    assert new_editor.editors[0][1] == 'sphere'
