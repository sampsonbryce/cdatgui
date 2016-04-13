import pytest
import vcs, cdms2
from PySide import QtGui, QtCore
from cdatgui.editors.secondary.preview.text import TextStylePreviewWidget


def test_preview():
    prev = TextStylePreviewWidget()
    text = vcs.createtext()
    text.name = "test"
    prev.setTextObject(text)
    assert prev.textobj == text

    text.name = "pizza"
    prev.update()

    assert prev.textobj.name == "pizza"
