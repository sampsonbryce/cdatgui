from PySide import QtGui
import vcs
import re

tmpl_filter = re.compile("of\\d+")


class TemplateList(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(TemplateList, self).__init__(parent=parent)
        self.templates = [template for template in vcs.elements["template"].values() if tmpl_filter.search(template.name) is None]

        self.addItems([tmpl.name for tmpl in self.templates])

    def get_selected(self):
        ind = self.currentRow()
        if ind == -1:
            return None
        return self.templates[ind]
