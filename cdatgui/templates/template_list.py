from PySide import QtGui, QtCore
from . import get_templates
import re


class TemplateList(QtGui.QListView):
    changedSelection = QtCore.Signal()

    def __init__(self, parent=None):
        super(TemplateList, self).__init__(parent=parent)
        self.setModel(get_templates())
        self.setDragEnabled(True)

    def currentRow(self):
        if self.selectedIndexes():
            return self.selectedIndexes()[0].row()
        return -1

    def remove(self, tmpl):
        self.model().removeRows(self.model().indexOf(tmpl).row(), 1)

    def get_selected(self):
        ind = self.currentRow()
        if ind == -1:
            return None
        return self.model().templates[ind]

    def selectionChanged(self, *args, **kwargs):
        super(TemplateList, self).selectionChanged(*args, **kwargs)
        self.changedSelection.emit()
