import pytest
from cdatgui.bases.window_widget import BaseSaveWindowWidget
from cdatgui.editors.secondary.preview.line import LinePreviewWidget


class DummyClass(object):
    def __init__(self, name):
        self.name = name


@pytest.fixture
def window():
    base = BaseSaveWindowWidget()
    struct = DummyClass("test")
    base.object = struct
    preview = LinePreviewWidget()
    base.setPreview(preview)
    return base


def save(name):
    assert name == "test"


def save_as(name):
    assert name == "pizza"


def test_save(qtbot, window):
    base = window
    base.accepted.connect(save)
    base.accept()


def test_save_as(qtbot, window):
    base = window
    base.accepted.connect(save_as)
    base.saveAs()
    base.win.setTextValue("pizza")
    base.win.accepted.emit()


def test_duplicate_preview(window):
    new_prev = LinePreviewWidget()
    window.setPreview(new_prev)
    assert window.vertical_layout.count() == 2
