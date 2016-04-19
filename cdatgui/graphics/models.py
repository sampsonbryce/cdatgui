from PySide import QtCore
import vcs

mimetype = "application/x-vcs-gm"


class VCSGraphicsMethodModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(VCSGraphicsMethodModel, self).__init__(parent=parent)
        self.gm_types = sorted(vcs.graphicsmethodlist())
        self.gms = {gmtype: [el for el in vcs.elements[gmtype].values() if el.name[:1] != "__"]
                    for gmtype in vcs.graphicsmethodlist()}

    def add_gm(self, gm):
        parent_row = self.gm_types.index(vcs.graphicsmethodtype(gm))
        self.insertRows(self.rowCount(), 1, [gm], self.index(parent_row, 0))

    def indexOf(self, gmtype, gm):
        parent = self.gm_types.index(gmtype)
        actual = self.gms[gmtype].index(gm)
        return self.index(actual, 0, parent=self.index(parent, 0))

    def replace(self, index, gm):
        self.gms[vcs.graphicsmethodtype(gm)][index.row()] = gm
        self.dataChanged.emit(index, index)

    def get(self, index):
        return self.get_gm(index)

    def get_gm(self, index):
        return self.gms[index]

    def get_dropped(self, md):
        if mimetype not in md.formats():
            raise ValueError("Mime Data supplied is not from VCSGraphicsMethodModel")  # noqa

        parts = []
        for char in md.data(mimetype):
            parts.append(char)

        gm = "".join(parts)
        gm_type, gm_name = gm.split(":::")

        return vcs.elements[gm_type][gm_name]

    def index(self, row, col, parent=QtCore.QModelIndex()):
        if parent.isValid():
            # Grab the child of parent
            gm_type = self.gm_types[parent.row()]
            pointer = self.gms[gm_type][row]
        else:
            pointer = self.gm_types[row]

        return self.createIndex(row, col, pointer)

    def parent(self, qmi):
        if qmi.internalPointer() in self.gm_types:
            # Root level item, no work required
            return QtCore.QModelIndex()

        for ind, gtype in enumerate(self.gm_types):
            if qmi.internalPointer() in self.gms[gtype]:
                return self.index(ind, 0)

        return QtCore.QModelIndex()

    def columnCount(self, qmi=QtCore.QModelIndex()):
        return 1

    def insertRows(self, row, count, gms, parent=QtCore.QModelIndex()):
        if parent.isValid() is False:
            raise ValueError("Can't insert new Graphics Method Types")

        parent_name = self.data(parent)
        self.beginInsertRows(parent, row, row + count)
        self.gms[parent_name] = self.gms[parent_name][:row] + gms + self.gms[parent_name][row:]
        self.endInsertRows()

    def rowCount(self, modelIndex=QtCore.QModelIndex()):
        if modelIndex.isValid() is False:
            return len(self.gm_types)
        if modelIndex.parent().isValid() is False:
            return len(self.gms[self.gm_types[modelIndex.row()]])
        return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        parent = index.parent()
        if parent.isValid():
            # index is a GM
            gtype = parent.internalPointer()
            gm = self.gms[gtype][index.row()]
            return unicode(gm.name)
        else:
            return unicode(self.gm_types[index.row()])

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return u"Graphics Method"

    def flags(self, index):
        if index.isValid() and index.parent().isValid():
            return QtCore.Qt.ItemIsDragEnabled | super(VCSGraphicsMethodModel, self).flags(index)  # noqa
        else:
            return super(VCSGraphicsMethodModel, self).flags(index)

    def mimeTypes(self):
        return [mimetype]

    def mimeData(self, indices):
        md = QtCore.QMimeData()

        gm_type = self.data(indices[0].parent())
        gm = self.gms[gm_type][indices[0].row()]

        ba = QtCore.QByteArray(gm_type + ":::" + gm.name)

        md.setData(mimetype, ba)
        return md
