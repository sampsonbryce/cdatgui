from PySide import QtGui
from models import VCSTemplateListModel
import re

tmpl_filter = re.compile("of\\d+")


class TemplateList(QtGui.QListView):
    def __init__(self, parent=None):
        super(TemplateList, self).__init__(parent=parent)
        self.setModel(VCSTemplateListModel(tmpl_filter=tmpl_filter))
        self.setDragEnabled(True)

    def get_selected(self):
        ind = self.currentRow()
        if ind == -1:
            return None
        return self.model().templates[ind]
