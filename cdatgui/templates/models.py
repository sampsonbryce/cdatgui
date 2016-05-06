from PySide import QtCore
import vcs
import re

tmpl_group_rx = re.compile("(.*)(\d+)of(\d+)(.*)")
mimetype = "application/x-vcs-template"


class VCSTemplateListModel(QtCore.QAbstractListModel):
    def __init__(self, tmpl_filter=None, parent=None):
        super(VCSTemplateListModel, self).__init__(parent=parent)
        if tmpl_filter is not None:
            self.templates = [template for template in vcs.elements["template"].values() if
                              tmpl_filter.search(template.name) is None]
        else:
            self.templates = vcs.elements["template"].values()

        def template_key(tmpl):
            m = tmpl_group_rx.search(tmpl.name)
            if m is None:
                return tmpl.name.lower()
            else:
                return (m.group(1) + m.group(3) + m.group(2) + m.group(4)).lower()

        self.templates = sorted(self.templates, key=template_key)

    def replace(self, ind, tmpl):
        if ind < len(self.templates):
            self.templates[ind] = tmpl
            self.dataChanged.emit(ind, ind)
        else:
            raise IndexError("Index %d out of range." % ind)

    def get(self, ind):
        return self.templates[ind]

    def indexOf(self, template):
        for i, t in enumerate(self.templates):
            if t.name == template.name:
                return self.index(i, 0)
        return QtCore.QModelIndex()

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
        self.beginInsertRows(parent, row, row + count - 1)
        self.templates = self.templates[:row] + templates + self.templates[row:]
        self.endInsertRows()

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self.templates.pop(row)
        self.endRemoveRows()

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
