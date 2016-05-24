from PySide import QtCore
from cdatgui.bases.list_model import ListModel
import cdms2


class CDMSVariableListModel(ListModel):

    remove_variable = ListModel.remove

    def get_variable(self, var_name_or_index):
        if isinstance(var_name_or_index, int):
            return self.get(var_name_or_index)
        else:
            for v in self.values:
                if v[0] == var_name_or_index:
                    return v[1]
            raise ValueError("No variable found with ID %s" % var_name_or_index)

    def get(self, ind):
        return self.values[ind][1]

    def get_variable_label(self, var):
        for label, value in self.values:
            try:
                if value == var:
                    return label
            except (ValueError, cdms2.error.CDMSError):
                pass

    def append(self, variable):
        super(CDMSVariableListModel, self).append((variable.id, variable))

    add_variable = append

    def update_variable(self, variable, label):
        for ind, var in enumerate(self.values):
            if var[0] == label:
                break
        else:
            raise ValueError("No variable found with ID %s" % variable.id)
        self.replace(ind, variable)

    def replace(self, index, value):
        if index < len(self.values):
            super(CDMSVariableListModel, self).replace(index, (self.values[index][0], value))
        else:
            raise IndexError("Index %d out of range." % index)

    def variable_exists(self, variable_or_id):
        if isinstance(variable_or_id, str):
            v_id = variable_or_id
        else:
            v_id = variable_or_id.id
        for var in self.values:
            if var[0] == v_id:
                return True
        return False

    def get_dropped(self, md):
        variables = []

        if "application/x-cdms-variable-list" not in md.formats():
            raise ValueError("Mime Data supplied is not from CDMSVariableListModel")
        parts = []
        for char in md.data("application/x-cdms-variable-list"):
            parts.append(char)

        indices = "".join(parts).split(",")
        variables = [self.values[int(ind)][1].var for ind in indices]
        return variables

    def format_for_display(self, variable):
        return variable[0]

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

    def format_for_icon(self, value):
        return None
