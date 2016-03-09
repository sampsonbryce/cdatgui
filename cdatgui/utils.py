import os
from PySide import QtGui


def data_file(filename):
    path = os.path.join(os.path.split(__file__)[0], filename)
    if os.path.exists(path):
        return path
    else:
        raise IOError("File '%s' not found" % filename)

def pattern_thumbnail(index):
    return icon("pattern_thumbs/pattern_%d.png" % index)

def icon(icon_name):
    return QtGui.QIcon(data_file(os.path.join("resources", icon_name)))


class Spacer(QtGui.QWidget):
    def __init__(self, width=None, parent=None):
        """
        A simple spacer object that will expand to fill all space
        or be of a defined width. No tests needed.
        """
        super(Spacer, self).__init__(parent=parent)

        if width is None:
            self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                               QtGui.QSizePolicy.Expanding)
        else:
            self.resize(width, 1)


def has_flag(flags, flag):
    return flags & flag


def accum_flags(flags):
    base = 0
    for flag in flags:
        base |= flag
    return base


def label(text):
    l = QtGui.QLabel(unicode(text))
    return l


def header_label(text):
    l = label(text)
    return l
