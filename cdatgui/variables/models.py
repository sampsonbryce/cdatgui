from PySide import QtCore
from cdatgui.bases.list_model import ListModel


class CDMSVariableListModel(ListModel):

    add_variable = ListModel.append
    remove_variable = ListModel.remove

    def get_variable(self, var_name_or_index):
        if isinstance(var_name_or_index, int):
            return self.get(var_name_or_index)
        else:
            for v in self.values:
                if v.id == var_name_or_index:
                    return v
            raise ValueError("No variable found with ID %s" % var_name_or_index)

    def update_variable(self, variable):
        for ind, var in enumerate(self.values):
            if var.id == variable.id:
                break
        else:
            raise ValueError("No variable found with ID %s" % variable.id)
        self.replace(ind, variable)

    def variable_exists(self, variable):
        print "CHECKING IF EXISTS:", variable
        for var in self.values:
            print "IDS:", var.id, variable.id
            if var.id == variable.id:
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
        variables = [self.values[int(ind)].var for ind in indices]

        return variables

    def format_for_display(self, variable):
        return unicode(variable.id)

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
