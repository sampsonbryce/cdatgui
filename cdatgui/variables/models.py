from PySide import QtCore


class CDMSVariableListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(CDMSVariableListModel, self).__init__(parent=parent)
        self.variables = []

    def add_variable(self, variable):
        self.insertRows(self.rowCount(), 1, [variable])

    def get_variable(self, index):
        return self.variables[index]

    def get_dropped(self, md):
        variables = []

        if "application/x-cdms-variable-list" not in md.formats():
            raise ValueError("Mime Data supplied is not from CDMSVariableListModel")
        parts = []
        for char in md.data("application/x-cdms-variable-list"):
            parts.append(char)

        indices = "".join(parts).split(",")
        variables = [self.variables[int(ind)].var for ind in indices]

        return variables

    def insertRows(self, row, count, variables, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count)
        self.variables = self.variables[:row] + variables + self.variables[row:]
        self.endInsertRows()

    def rowCount(self, modelIndex=None):
        return len(self.variables)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return unicode(self.variables[index.row()].id)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return u"Variable Name"

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsDragEnabled | super(CDMSVariableListModel, self).flags(index)
        else:
            return super(CDMSVariableListModel, self).flags(index)

    def mimeTypes(self):
        return ["application/x-cdms-variable-list"]

    def mimeData(self, indices):
        md = QtCore.QMimeData()

        rows = []

        for index in indices:
            rows.append(str(index.row()))

        ba = QtCore.QByteArray(",".join(rows))

        md.setData("application/x-cdms-variable-list", ba)
        return md
