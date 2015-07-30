from PySide import QtGui
from cdms_file_tree import CDMSFileTree


class AddDialog(QtGui.QDialog):
    def __init__(self, parent=None, f=0):
        super(AddDialog, self).__init__(parent=parent, f=f)
        self.setModal(True)

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

        tree_wrapper = QtGui.QGroupBox()

        # Should persist available files here...
        self.tree = CDMSFileTree()
        tree_layout = QtGui.QVBoxLayout()
        tree_layout.addWidget(self.tree)
        tree_wrapper.setLayout(tree_layout)
        tree_wrapper.setTitle(u"Recent Datasets")

        horiz.addWidget(tree_wrapper)

    def selected_variables(self):
        return self.tree.get_selected()
