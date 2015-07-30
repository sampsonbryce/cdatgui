from cdatgui.bases import StaticDockWidget
from PySide import QtCore
from cdatgui.toolbars import AddEditRemoveToolbar
from variable_add import AddDialog


class VariableWidget(StaticDockWidget):

    def __init__(self, parent=None, flags=0):
        super(VariableWidget, self).__init__(u"Variables", parent, flags)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]

        self.add_dialog = AddDialog(self)
        self.add_dialog.accepted.connect(self.add_variable)

        self.setTitleBarWidget(AddEditRemoveToolbar("Variables",
                                                    self,
                                                    self.add_dialog.show,
                                                    self.edit_variable,
                                                    self.remove_variable))

        # self.setWidget(widget)

    def add_variable(self):
        new_variables = self.add_dialog.selected_variables()
        for var in new_variables:
            print var.id

    def edit_variable(self):
        # Edit variable dialog
        print "Edit variable"

    def remove_variable(self):
        # Confirm removal dialog
        print "Remove Variable"
