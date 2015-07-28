import os
from PySide import QtGui


def data_file(filename):
    path = os.path.join(os.path.split(__file__)[0], filename)
    if os.path.exists(path):
        return path
    else:
        raise IOError("File '%s' not found" % filename)


def icon(icon_name):
    return QtGui.QIcon(data_file(os.path.join("resources", icon_name)))


class Spacer(QtGui.QWidget):
    def __init__(self, width=None, parent=None):
        super(Spacer, self).__init__(parent=parent)

        if width is None:
            self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                               QtGui.QSizePolicy.Expanding)
        else:
            self.resize(width, 1)
