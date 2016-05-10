import pytest, vcs, cdms2, os
# from cdatgui.graphics.dialog import *
# from cdatgui.cdat.metadata import FileMetadataWrapper
# from cdatgui.editors import boxfill, isoline, cdat1d
from cdatgui.graphics import get_gms
from cdatgui.graphics.graphics_method_widget import CreateGM, EditGmDialog
from PySide import QtCore, QtGui


@pytest.fixture
def creategm_dialog():
    cgm = CreateGM(['boxfill', 'a_boxfill'])
    return cgm


@pytest.fixture
def editgm_dialog_store():
    egmd = EditGmDialog('boxfill', 'a_boxfill')
    return egmd


@pytest.fixture
def editgm_dialog_nostore():
    egmd = EditGmDialog('boxfill', 'a_boxfill', False)
    return egmd


def test_createGM(qtbot, creategm_dialog):
    assert creategm_dialog.gm_type_combo.currentText() == 'boxfill'
    assert creategm_dialog.gm_instance_combo.currentText() == 'a_boxfill'

    # assure its passing in the correct value to the customize dialog
    # print "editing gm"
    creategm_dialog.editGM()
    assert creategm_dialog.edit_dialog.gtype == 'boxfill'
    assert creategm_dialog.edit_dialog.ginstance == 'a_boxfill'
    # print "emitting accept"
    # import pdb; pdb.set_trace()
    creategm_dialog.edit_dialog.accepted.emit()
    # print "after emitting accept"

    creategm_dialog.gm_type_combo.setCurrentIndex(creategm_dialog.gm_type_combo.findText('isoline'))
    assert creategm_dialog.gm_instance_combo.currentText() == 'default'
    assert creategm_dialog.gm_instance_combo.rootModelIndex().row() == 6
    assert creategm_dialog.edit_dialog is None
    # print "adjusting root"

    # assert the validator type gets updated
    assert creategm_dialog.edit.validator().gm_type == 'isoline'

    assert creategm_dialog.save_button.isEnabled() == False
    creategm_dialog.setTextValue('new_isoline')
    assert creategm_dialog.save_button.isEnabled() == True
    creategm_dialog.createGM()

    assert vcs.getisoline('new_isoline') in get_gms().gms['isoline']


def test_createGM_using_customize_gm(qtbot, creategm_dialog):
    creategm_dialog.editGM()
    assert creategm_dialog.edit_dialog.gtype == 'boxfill'
    assert creategm_dialog.edit_dialog.ginstance == 'a_boxfill'
    print "loaded edit gm"
    creategm_dialog.edit_dialog.gm.projection = 'robinson'
    creategm_dialog.edit_dialog.reject()
    creategm_dialog.setTextValue('new_boxfill')
    creategm_dialog.createGM()
    print "rejected gm create"

    assert vcs.getboxfill('new_boxfill') in get_gms().gms['boxfill']
    assert vcs.getboxfill('new_boxfill').projection == 'linear'

    creategm_dialog.editGM()
    assert creategm_dialog.edit_dialog.gtype == 'boxfill'
    assert creategm_dialog.edit_dialog.ginstance == 'a_boxfill'

    creategm_dialog.edit_dialog.gm.projection = 'robinson'
    print "EDITED GM", creategm_dialog.edit_dialog.gm.list()
    creategm_dialog.edit_dialog.accepted.emit()

    # test for reopening
    creategm_dialog.editGM()
    assert creategm_dialog.edit_dialog.gm.projection == 'robinson'
    print "REOPENED NON EDITED GM", creategm_dialog.edit_dialog.gm.list()
    creategm_dialog.edit_dialog.accepted.emit()

    creategm_dialog.setTextValue('new_boxfill2')
    creategm_dialog.createGM()

    assert vcs.getboxfill('new_boxfill2') in get_gms().gms['boxfill']
    assert vcs.getboxfill('new_boxfill2').projection == 'robinson'


def test_EditGmDialogStore(qtbot, editgm_dialog_store):
    editgm_dialog_store.rejected.emit()
    assert editgm_dialog_store.edit_tmpl_name not in vcs.listelements('template')
    assert editgm_dialog_store.edit_gm_name not in vcs.listelements('boxfill')


def test_EditGmDialogNoStore(qtbot, editgm_dialog_nostore):
    dialog = editgm_dialog_nostore
    orig_gm = vcs.getboxfill(dialog.ginstance)
    dialog.createGM()
    new_gm = vcs.getboxfill(dialog.ginstance)
    assert new_gm != orig_gm
    assert new_gm in get_gms().gms[dialog.gtype]
    assert orig_gm not in get_gms().gms[dialog.gtype]
    assert editgm_dialog_nostore.edit_tmpl_name not in vcs.listelements('template')
    assert editgm_dialog_nostore.edit_gm_name not in vcs.listelements('boxfill')
