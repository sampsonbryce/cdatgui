import pytest, vcs, cdms2, os
from cdatgui.editors.widgets.multi_line_editor import MultiLineEditor
from cdatgui.editors.widgets.multi_text_editor import MultiTextEditor
from cdatgui.cdat.metadata import FileMetadataWrapper
from cdatgui.editors.model.isoline_model import IsolineModel
from cdatgui.vcsmodel import get_lines, get_textstyles


@pytest.fixture
def line_editor():
    """
    Multi Editors are only being tested with set levels due to odd behavior with autolabels
    that is waiting for merge
    """
    editor = MultiLineEditor()
    gm = vcs.getisoline('a_isoline')
    gm.levels = range(10, 80, 10)
    editor.setObject(IsolineModel(gm, get_var()))
    return editor, gm


@pytest.fixture
def text_editor():
    """
    Multi Editors are only being tested with set levels due to odd behavior with autolabels
    that is waiting for merge
    """
    editor = MultiTextEditor()
    gm = vcs.getisoline('a_isoline')
    gm.levels = range(10, 80, 10)
    editor.setObject(IsolineModel(gm, get_var()))
    return editor, gm


def get_var():
    f = cdms2.open(os.path.join(vcs.sample_data, 'clt.nc'))
    f = FileMetadataWrapper(f)
    s = f('clt')
    return s


def test_MultiLineEditor(qtbot, line_editor):
    editor = line_editor[0]
    gm = line_editor[1]
    for combo in editor.line_combos:
        assert combo.currentIndex() != -1

    editor.line_combos[2].setCurrentIndex(10)
    print editor.line_combos[2].model().elements
    print editor.isoline_model.line
    assert editor.isoline_model.line[2] == 'pink'

    editor.editLine(6)
    qtbot.addWidget(editor.line_editor)
    assert editor.line_editor
    assert isinstance(editor.line_editor.object, vcs.line.Tl)

    # simulate editing a line and updating it
    l = vcs.createline('dummy')
    l.color = [55]
    l.type = ['dash-dot']
    l.width = [8]
    get_lines().updated('dummy')

    editor.update(4, 'dummy')
    assert editor.line_combos[4].currentText() == 'dummy'

    editor.accept()

    # check and see if the isoline was updated when combo changed and ok was pressed
    assert gm.linecolors[2] == 254
    assert gm.linewidths[2] == 2
    assert vcs.getline(gm.line[2]).name == 'pink'
    assert vcs.getline(gm.line[2]).type == ['dash']

    assert gm.linecolors[4] == 55
    assert gm.linewidths[4] == 8
    assert vcs.getline(gm.line[4]).name == 'dummy'
    assert vcs.getline(gm.line[4]).type == ['dash-dot']


def test_MultiTextEditor(qtbot, text_editor):
    editor = text_editor[0]
    gm = text_editor[1]
    for combo in editor.text_combos:
        assert combo.currentIndex() != -1

    editor.text_combos[2].setCurrentIndex(3)
    assert editor.isoline_model.text[2] == 'qa'

    editor.editText(1)
    qtbot.addWidget(editor.text_editor)
    assert editor.text_editor
    assert isinstance(editor.text_editor.object, vcs.textcombined.Tc)

    # simulate editing a line and updating it
    tc = vcs.createtextcombined('dummy')
    tc.angle = 30
    tc.font = 'Chinese'
    tc.halign = 1
    tc.valign = 1
    tc.height = 24
    get_textstyles().updated('dummy')

    editor.update(3, 'dummy')
    assert editor.text_combos[3].currentText() == 'dummy'

    editor.accept()

    # check and see if the isoline was updated when combo changed and ok was pressed
    assert vcs.gettextcombined(gm.text[3], gm.text[3]).name == 'dummy:::dummy'
    assert vcs.gettextcombined(gm.text[3], gm.text[3]).font == 8  # 'Chinese'
    assert vcs.gettextcombined(gm.text[3], gm.text[3]).halign == 1
    assert vcs.gettextcombined(gm.text[3], gm.text[3]).valign == 1
    assert vcs.gettextcombined(gm.text[3], gm.text[3]).height == 24
