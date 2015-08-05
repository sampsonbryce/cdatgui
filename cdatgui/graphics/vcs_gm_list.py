import vcs
from PySide import QtGui, QtCore


class GraphicsMethodList(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        super(GraphicsMethodList, self).__init__(parent=parent)
        # Get all of the available graphics methods
        self.types = {gmtype: vcs.elements[gmtype]
                      for gmtype in vcs.graphicsmethodlist()}

        self.setColumnCount(1)
        self.header().close()

        for gmtype in self.types:
            item = QtGui.QTreeWidgetItem()
            item.setText(0, gmtype)
            self.addTopLevelItem(item)
            for gm in self.types[gmtype]:
                child = QtGui.QTreeWidgetItem()
                child.setText(0, gm)
                item.addChild(child)

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
