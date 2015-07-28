from PySide import QtGui


class AddDialog(QtGui.QDialog):
    def __init__(self, parent=None, f=0):
        super(AddDialog, self).__init__(parent=parent, f=f)
