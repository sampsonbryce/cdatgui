from PySide import QtGui
import vcs


class TemplateList(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(TemplateList, self).__init__(parent=parent)
        self.templates = vcs.elements["template"].values()

        self.addItems([tmpl.name for tmpl in self.templates])

    def get_selected(self):
        ind = self.currentRow()
        if ind == -1:
            return None
        return self.templates[ind]
