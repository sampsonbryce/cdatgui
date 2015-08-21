from PySide import QtCore
import vcs

mimetype = "application/x-vcs-template"


class VCSTemplateListModel(QtCore.QAbstractListModel):
    def __init__(self, tmpl_filter=None, parent=None):
        super(VCSTemplateListModel, self).__init__(parent=parent)
        if tmpl_filter is not None:
            self.templates = [template for template in vcs.elements["template"].values() if tmpl_filter.search(template.name) is None]
        else:
            self.templates = vcs.elements["template"].values()

    def add_template(self, template):
        self.insertRows(self.rowCount(), 1, [template])

    def get_template(self, index):
        return self.templates[index]

    def get_dropped(self, md):
        if "application/x-vcs-template" not in md.formats():
            raise ValueError("Mime Data supplied is not from VCSTemplateListModel")

        parts = []
        for char in md.data(mimetype):
            parts.append(char)

        template_name = "".join(parts)

        return vcs.elements["template"][template_name]

    def insertRows(self, row, count, templates, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count)
        self.templates = self.templates[:row] + templates + self.templates[row:]
        self.endInsertRows()

    def rowCount(self, modelIndex=None):
        return len(self.templates)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return unicode(self.templates[index.row()].name)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return u"Template Name"

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsDragEnabled | super(VCSTemplateListModel, self).flags(index)
        else:
            return super(VCSTemplateListModel, self).flags(index)

    def mimeTypes(self):
        return [mimetype]

    def mimeData(self, indices):
        md = QtCore.QMimeData()

        ba = QtCore.QByteArray(self.data(indices[0]))

        md.setData(mimetype, ba)
        return md
