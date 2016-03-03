import vcs, cdms2
from cdatgui.editors.secondary.preview.marker import MarkerPreviewWidget


def test_preview():
    prev = MarkerPreviewWidget()
    marker = vcs.createmarker("test")
    prev.setMarkerObject(marker)
    assert prev.markerobj == marker

    marker.type = "cross"
    prev.update()

    assert prev.markerobj.type == ["cross"]