from PySide import QtCore
import vcs

mimetype = "application/x-vcs-gm"


class VCSGraphicsMethodModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(VCSGraphicsMethodModel, self).__init__(parent=parent)
        self.gm_types = sorted(vcs.graphicsmethodlist())
        self.gms = {gmtype: [el for el in vcs.elements[gmtype].values() if el.name[:1] != "__"]
                    for gmtype in vcs.graphicsmethodlist()}
        self.next_id = 0
        self.keys = {}

    def add_gm(self, gm):
        parent_row = self.gm_types.index(vcs.graphicsmethodtype(gm))
        self.insertRows(self.rowCount(), 1, [gm], self.index(parent_row, 0))

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            # Can't remove graphics method types
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.gms[self.gm_types[parent.row()]][row:row + count]
        self.endRemoveRows()
        return True

    def indexOf(self, gmtype, gm):
        parent = self.gm_types.index(gmtype)
        for list_gm in self.gms[gmtype]:
            if list_gm.name == gm.name:
                actual = self.gms[gmtype].index(list_gm)
                break
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
            key = (parent.row(), row)
        else:
            key = (row, None)
        if key in self.keys:
            internalid = self.keys[key]
        else:
            internalid = self.next_id
            self.keys[key] = internalid
            self.next_id += 1
        return self.createIndex(row, col, internalid)

    def parent(self, qmi):
        if not qmi.isValid():
            return QtCore.QModelIndex()

        for key in self.keys:
            if qmi.internalId() == self.keys[key]:
                break
        else:
            return QtCore.QModelIndex()

        if key[1] is None:
            return QtCore.QModelIndex()
        else:
            return self.index(key[0], 0)

    def columnCount(self, qmi=QtCore.QModelIndex()):
        return 1

    def insertRows(self, row, count, gms, parent=QtCore.QModelIndex()):
        if parent.isValid() is False:
            raise ValueError("Can't insert new Graphics Method Types")

        parent_name = self.data(parent)
        self.beginInsertRows(parent, row, row + count - 1)
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

        for key in self.keys:
            if self.keys[key] == index.internalId():
                break
        gm_type = self.gm_types[key[0]]
        if key[1] is None:
            return unicode(gm_type)
        gm = self.gms[gm_type][key[1]]
        return unicode(gm.name)

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
