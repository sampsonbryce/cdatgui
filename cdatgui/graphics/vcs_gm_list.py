import vcs
from PySide import QtGui, QtCore
from cdatgui.graphics import get_gms


class GraphicsMethodList(QtGui.QTreeView):
    changedSelection = QtCore.Signal()

    def __init__(self, parent=None):
        super(GraphicsMethodList, self).__init__(parent=parent)
        self.setModel(get_gms())
        self.setDragEnabled(True)
        self.header().close()
        self.setIndentation(10)

    def get_selected(self):
        items = self.selectedIndexes()
        for selected in items:
            if not selected.parent().isValid():
                return [selected.data()]

            return [selected.parent().data(), selected.data()]
        return None

    def selectionChanged(self, selected, deselected):
        super(GraphicsMethodList, self).selectionChanged(selected, deselected)
        self.changedSelection.emit()
