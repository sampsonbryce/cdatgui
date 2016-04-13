import vcs, cdms2
from cdatgui.editors.secondary.preview.fillarea import FillPreviewWidget


def test_preview():

    prev = FillPreviewWidget()
    fill = vcs.createfillarea()
    prev.setFillObject(fill)
    assert prev.fillobj == fill

    fill.style = "hatch"
    prev.update()

    assert prev.fillobj.style == ["hatch"]

