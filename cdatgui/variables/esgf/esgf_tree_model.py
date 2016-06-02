from PySide import QtGui, QtCore


class ESGFDatasetTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, data=None, parent=None):
        super(ESGFDatasetTreeModel, self).__init__(parent=parent)
        if data is None:
            self.datasets = []
        else:
            self.datasets = data
        self.keys = {}
        self.inds_to_keys = {}
        self.next_id = 0

    def rowCount(self, model_index=QtCore.QModelIndex()):
        if not model_index.isValid():
            return len(self.datasets)
        if not model_index.parent().isValid():
            return len(self.datasets[model_index.row()]['variable_long_name'])
        return 0

    def get(self, index):
        return self.getData(index.row(), index.column(), index.parent())

    def columnCount(self, model_index=QtCore.QModelIndex()):
        return 1

    def parent(self, ind):
        for k, int_id in self.keys.iteritems():
            if int_id == ind.internalId():
                root_row = self.datasets[k[0]]
                if k[1] is None:
                    return QtCore.QModelIndex()
                else:
                    return self.index(k[0], 0)
        return QtCore.QModelIndex()

    def getData(self, row, col, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            if col == 0:
                return self.datasets[row].dataset_id
            else:
                return None
        else:
            if col == 1:
                return self.datasets[parent.row()].json['variable_long_name'][row]
            else:
                return None

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        k = self.inds_to_keys[index.internalId()]
        root_row = self.datasets[k[0]]
        if k[1] is not None:
            data = root_row["variable_long_name"][k[1]]
        else:
            data = root_row["id"]
        print "Got data", k
        return data

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
            self.inds_to_keys[internalid] = key
            self.next_id += 1
        print "Got index", key
        return self.createIndex(row, col, internalid)

    def insertRows(self, row, count, datasets, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        self.datasets.extend(datasets)
        self.endInsertRows()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return u"Results"

