import vcs
from PySide import QtCore


class VCSElementsModel(QtCore.QAbstractListModel):
    el_type = None

    def __init__(self, parent=None):
        self.elements = []
        self.isa = None
        self.get_el = None
        super(VCSElementsModel, self).__init__(parent)
        self.init_elements()

    def init_elements(self):
        self.elements = sorted((el for el in vcs.listelements(self.el_type) if el[:2] != "__"))

    def rowCount(self, parent=None):
        return len(self.elements)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        el_name = self.elements[index.row()]
        el_obj = self.get_el(el_name)
        if role == QtCore.Qt.DisplayRole:
            return el_name
        if role == QtCore.Qt.UserRole:
            return el_obj
        if role == QtCore.Qt.ToolTipRole:
            return self.tooltip(el_name, el_obj)
        return None

    def tooltip(self, name, obj):
        raise NotImplementedError("Subclasses must implement tooltip function.")

    def updated(self, el_name):
        try:
            ind = self.elements.index(el_name)
            model_ind = self.index(ind)
            self.dataChanged.emit(model_ind, model_ind)
        except ValueError:
            new_els = []
            insert_ind = -1
            insert_me = el_name
            for ind, name in enumerate(self.elements):
                if insert_me is not None and name > insert_me:
                    new_els.append(insert_me)
                    insert_ind = ind
                    insert_me = None
                new_els.append(name)

            if insert_ind == -1:
                new_els.append(el_name)
                insert_ind = len(self.elements)
            self.beginInsertRows(QtCore.QModelIndex(), insert_ind, insert_ind)
            self.elements = new_els
            self.endInsertRows()

    def remove(self, el_name):
        new_els = []
        remove_ind = -1
        remove_me = el_name
        for ind, name in enumerate(self.elements):
            if remove_me is not None and name == remove_me:
                remove_ind = ind
                remove_me = None
            else:
                new_els.append(name)

        if remove_ind == -1:
            return

        self.beginRemoveRows(QtCore.QModelIndex(), remove_ind, remove_ind)
        self.elements = new_els
        self.endRemoveRows()

