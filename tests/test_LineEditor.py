import pytest
import vcs, cdms2
from cdatgui.editors.secondary.editor.line import LineEditorWidget
from cdatgui.vcsmodel import get_lines


@pytest.fixture
def editor():
    editor = LineEditorWidget()
    line = vcs.getline('cyan')
    editor.setLineObject(line)
    return editor


def test_type(qtbot, editor):
    editor.updateType('dash')
    assert editor.object.type == ['dash']

    editor.accept()
    assert vcs.elements['line']['cyan'].type == ['dash']
    assert editor.newline_name not in vcs.listelements('line')


def test_color(qtbot, editor):
    editor.updateColor(55)
    assert editor.object.color == [55]

    editor.saveAs()
    editor.win.setTextValue('check')
    editor.accept()
    assert 'check' in vcs.listelements('line')
    assert vcs.elements['line']['check'].color == [55]

    del vcs.elements['line']['check']
    assert 'check' not in vcs.listelements('line')
    assert editor.newline_name not in vcs.listelements('line')


def test_width(qtbot, editor):
    editor.updateWidth(250)
    assert editor.object.width == [250]

    editor.accept()
    assert vcs.elements['line']['cyan'].width == [250]
    assert editor.newline_name not in vcs.listelements('line')

    get_lines().remove('check')
    get_lines().remove(editor.newline_name)
