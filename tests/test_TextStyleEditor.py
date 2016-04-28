import pytest
import re
import vcs
from PySide import QtCore, QtGui
from cdatgui.editors.secondary.editor.text import TextStyleEditorWidget
from cdatgui.vcsmodel import get_textstyles


@pytest.fixture
def editors():
    for name in ['header', 'header2', 'header3']:
        try:
            del vcs.elements['textcombined']['{0}:::{1}'.format(name, name)]
            del vcs.elements['texttable'][name]
            del vcs.elements['textorientation'][name]
        except:
            print "didnt delete all"

    edit1 = TextStyleEditorWidget()
    t = vcs.createtext('header')
    edit1.setTextObject(t)

    edit2 = TextStyleEditorWidget()
    t = vcs.createtext('header2')
    t.valign = 0
    t.halign = 1
    edit2.setTextObject(t)

    edit3 = TextStyleEditorWidget()
    t = vcs.createtext('header3')
    t.valign = 4
    t.halign = 2
    edit3.setTextObject(t)

    return edit1, edit2, edit3


def save_check(name):
    # assert name in vcs.listelements('textcombined')
    assert re.match("header[0-9]*", name)


def test_save(qtbot, editors):
    for editor in editors:

        editor.saved.connect(save_check)
        editor.save()


def test_alignment(editors):
    for editor in editors:
        # test valign
        editor.updateButton(editor.va_group.buttons()[0])
        assert editor.object.valign == 0

        editor.updateButton(editor.va_group.buttons()[2])
        assert editor.object.valign == 4

        editor.updateButton(editor.va_group.buttons()[1])
        assert editor.object.valign == 2

        # test halign
        editor.updateButton(editor.ha_group.buttons()[2])
        assert editor.object.halign == 2

        editor.updateButton(editor.ha_group.buttons()[1])
        assert editor.object.halign == 1

        editor.updateButton(editor.ha_group.buttons()[0])
        assert editor.object.halign == 0


def test_angle(editors):
    for editor in editors:

        assert editor.object.angle == 0

        editor.updateAngle(50)
        assert editor.object.angle == 50

        editor.updateAngle(440)
        assert editor.object.angle == 80


def test_font(editors):
    for editor in editors:
        editor.updateFont("Helvetica")
        assert editor.object.font == 4

        editor.updateFont("Chinese")
        assert editor.object.font == 8


def test_size(editors):
    for editor in editors:
        assert editor.object.height == 14

        editor.updateSize(50)
        assert editor.object.height == 50


def saveas_check(name):
    assert name == "test.txt"


def test_saveas(qtbot, editors):
    for editor in editors:

        editor.saved.connect(saveas_check)
        editor.saveAs()

        try:
            print editor.win
        except:
            print "Did not create save as dialog"
            assert 0

        editor.win.setTextValue("test.txt")
        qtbot.keyPress(editor.win, QtCore.Qt.Key_Enter)
        assert "test.txt" in vcs.listelements('texttable')
        assert "test.txt" in vcs.listelements('textorientation')
        assert "test.txt" in get_textstyles().elements
    assert False
