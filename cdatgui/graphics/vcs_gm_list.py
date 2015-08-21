import vcs
from PySide import QtGui, QtCore
from models import VCSGraphicsMethodModel


class GraphicsMethodList(QtGui.QTreeView):
    def __init__(self, parent=None):
        super(GraphicsMethodList, self).__init__(parent=parent)
        self.setModel(VCSGraphicsMethodModel())
        self.setDragEnabled(True)
        self.header().close()
        self.setIndentation(10)

    def get_selected(self):
        items = self.selectedItems()
        sel = None

        for selected in items:
            if selected.parent() is None:
                continue

            p = selected.parent()

            t = self.types[p.text(0)]
            gm = t[selected.text(0)]
            sel = gm
            break

        return sel
