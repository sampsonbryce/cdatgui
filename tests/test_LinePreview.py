import pytest
import vcs, cdms2
from PySide import QtGui, QtCore
from cdatgui.editors.secondary.preview.line import LinePreviewWidget


def test_preview():
    prev = LinePreviewWidget()
    line = vcs.createline()
    prev.setLineObject(line)
    assert prev.lineobj == line

    line.type = "dot"
    prev.update()

    assert prev.lineobj.type == ["dot"]