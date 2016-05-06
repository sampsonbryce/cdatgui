from PySide import QtCore


class ListModel(QtCore.QAbstractListModel):
    listUpdated = QtCore.Signal()

    def __init__(self, parent=None):
        super(ListModel, self).__init__(parent=parent)
        # Simplify the API a bit
        self.rowsInserted.connect(self.updated_anything)
        self.rowsRemoved.connect(self.updated_anything)
        self.rowsMoved.connect(self.updated_anything)
        self.dataChanged.connect(self.updated_anything)
        self.modelReset.connect(self.updated_anything)
        self.values = []

    def updated_anything(self, *args):
        self.listUpdated.emit()

    def append(self, value):
        self.insertRows(self.rowCount(), 1, [value])

    def get(self, index):
        return self.values[index]

    def replace(self, index, value):
        self.values[index] = value
        ind = self.index(index, 0)
        self.dataChanged.emit(ind, ind)

    def remove(self, ind):
        return self.removeRows(ind, 1)

    def clear(self):
        self.removeRows(0, len(self.values))

    def insertRows(self, row, count, values, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count)
        self.values = self.values[:row] + values + self.values[row:]
        self.endInsertRows()

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self.values = self.values[:row] + self.values[row + count:]
        self.endRemoveRows()
        return True

    def rowCount(self, modelIndex=None):
        return len(self.values)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.format_for_display(self.values[index.row()])
        if role == QtCore.Qt.DecorationRole:
            return self.format_for_icon(self.values[index.row()])

    def format_for_display(self, value):
        raise NotImplementedError("format_for_display not implemented")

    def format_for_icon(self, value):
        raise NotImplementedError("format_for_icon not implemented")
