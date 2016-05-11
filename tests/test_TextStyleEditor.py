import pytest
import vcs
from PySide import QtCore, QtGui
from cdatgui.editors.secondary.editor.text import TextStyleEditorWidget
from cdatgui.vcsmodel import get_textstyles


@pytest.fixture
def editor():
    print "in editor"
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

    return edit1


def save_check(name):
    assert name == 'header'


def test_alignment(qtbot, editor):

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

    # test save as well
    editor.saved.connect(save_check)
    editor.accept()


def test_angle(editor):
    assert editor.object.angle == 0

    editor.updateAngle(50)
    assert editor.object.angle == 50

    editor.updateAngle(440)
    assert editor.object.angle == 80

    editor.accept()


def test_font(editor):
    editor.updateFont("Helvetica")
    assert editor.object.font == 4

    editor.updateFont("Chinese")
    assert editor.object.font == 8

    editor.accept()


def test_size(editor):
    assert editor.object.height == 14

    editor.updateSize(50)
    assert editor.object.height == 50

    editor.accept()


def saveas_check(name):
    assert name == "test.txt"


def test_saveas(qtbot, editor):

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

