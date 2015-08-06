from PySide import QtGui
from cdms_file_tree import CDMSFileTree
from cdatgui.toolbars import AddEditRemoveToolbar
from cdms_file_chooser import CDMSFileChooser


class AddDialog(QtGui.QDialog):
    def __init__(self, parent=None, f=0):
        super(AddDialog, self).__init__(parent=parent, f=f)

        wrap = QtGui.QVBoxLayout()

        horiz = QtGui.QHBoxLayout()

        wrap.addLayout(horiz, 10)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                         QtGui.QDialogButtonBox.Cancel)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        ok = buttons.button(QtGui.QDialogButtonBox.StandardButton.Ok)
        cancel = buttons.button(QtGui.QDialogButtonBox.StandardButton.Cancel)

        ok.setDefault(True)
        cancel.setDefault(False)

        wrap.addWidget(buttons)

        self.setLayout(wrap)

        # Should persist available files here...
        self.tree = CDMSFileTree()
        tree_layout = QtGui.QVBoxLayout()
        toolbar = AddEditRemoveToolbar(u"Available Files",
                                       add_action=self.add_file,
                                       remove_action=self.remove_file)

        tree_layout.addWidget(toolbar, 0)
        tree_layout.addWidget(self.tree, 10)

        horiz.addLayout(tree_layout, 2)

        self.chooser = CDMSFileChooser()
        self.chooser.accepted.connect(self.added_files)

    def selected_variables(self):
        return self.tree.get_selected()

    def add_file(self):
        self.chooser.show()  # pragma: no cover

    def added_files(self):
        files = self.chooser.get_selected()
        for cdmsfile in files:
            self.tree.add_file(cdmsfile)

    def remove_file(self):
        pass  # pragma: no cover
