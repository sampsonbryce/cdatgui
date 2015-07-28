from cdatgui.bases import StaticDockWidget
from PySide import QtCore, QtGui
from cdatgui.toolbars import AddEditRemoveToolbar
from cdms_file_tree import CDMSFileTree


class VariableWidget(StaticDockWidget):

    def __init__(self, parent=None, flags=0):
        super(VariableWidget, self).__init__(u"Variables", parent, flags)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]
        self.setTitleBarWidget(AddEditRemoveToolbar(u"Variables",
                                                    self,
                                                    self.add_variable,
                                                    self.edit_variable,
                                                    self.remove_variable))

        self.tree = CDMSFileTree(self)
        self.setWidget(self.tree)

    def add_variable(self):
        fd = QtGui.QFileDialog.getOpenFileName(self, u"Select netCDF file")[0]
        self.tree.add_file(fd)

    def edit_variable(self):
        # Edit variable dialog
        print "Edit Variable"

    def remove_variable(self):
        # Confirm removal dialog
        print "Remove Variable"
