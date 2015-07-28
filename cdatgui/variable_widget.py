from static_docked import StaticDockWidget
from PySide import QtCore
from toolbars import AddEditRemoveToolbar


class VariableWidget(StaticDockWidget):

    def __init__(self, parent=None, flags=0):
        super(VariableWidget, self).__init__(u"Variables", parent, flags)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]
        self.setTitleBarWidget(AddEditRemoveToolbar(u"Variables",
                                                    self,
                                                    self.add_variable,
                                                    self.edit_variable,
                                                    self.remove_variable))

    def add_variable(self):
        print "Add"

    def edit_variable(self):
        print "Edit"

    def remove_variable(self):
        print "Remove"
