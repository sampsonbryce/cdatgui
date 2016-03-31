import vcs
from PySide import QtCore


def find_runs(indices):
    """
    Reduces indices to bounded sets that describe the same indices.

    :param indices: List of indices
    :return: List of pairs of start/last indices
    """
    runs = []
    last_ind = 0
    start_ind = None
    for i in sorted(indices):
        if start_ind is not None:
            # We're looking at a run
            if i - 1 != last_ind:
                runs.append((start_ind, last_ind))
                start_ind = i
        else:
            start_ind = i
        last_ind = i

    last_run = start_ind, last_ind
    if start_ind is not None and (len(runs) == 0 or runs[-1] != last_run):
        runs.append(last_run)

    return runs


def diff_indices(a, b):
    set_a = set(a)
    set_b = set(b)

    diff = set_a - set_b
    indices = [a.index(el) for el in diff]
    return indices


class VCSElementsModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        self.el_type = None
        # Use appropriate vcs functions
        self.isa = None
        self.get_el = None
        self._elements = []
        super(VCSElementsModel, self).__init__(parent)

    def get_new_elements(self):
        return sorted([el for el in vcs.listelements(self.el_type) if el[:2] != "__"])

    @property
    def elements(self):
        """
        Fetch the elements associated with this model.

        :return: A sorted list of properly named elements
        """

        new_elements = self.get_new_elements()

        if new_elements != self._elements:
            # Diff the two sets and adjust _elements appropriately

            removed_indices = diff_indices(self._elements, new_elements)
            removed_runs = find_runs(removed_indices)
            offset = 0
            for run in removed_runs:
                first, last = run
                first -= offset
                last -= offset
                self.beginRemoveRows(QtCore.QModelIndex(), first, last)
                self._elements = self._elements[:first] + self._elements[last + 1:] if last + 1 < len(self._elements) else []
                self.endRemoveRows()
                offset += last - first + 1

            added_indices = diff_indices(new_elements, self._elements)
            added_runs = find_runs(added_indices)
            offset = 0
            for run in added_runs:
                first, last = run
                count = last - first + 1
                el_first = first + offset
                self.beginInsertRows(QtCore.QModelIndex(), first, count)
                self._elements = self._elements[:el_first] + new_elements[first:last + 1] + self._elements[el_first:]
                self.endInsertRows()
                offset += count
        return self._elements

    def rowCount(self, parent=None):
        return len(self._elements)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        el_name = self._elements[index.row()]
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
        ind = self.elements.index(el_name)
        model_ind = self.index(ind)
        self.dataChanged.emit(model_ind, model_ind)
