from PySide import QtGui, QtCore

import re
from functools import partial

from cdatgui.toolbars import AddEditRemoveToolbar
from cdms_file_chooser import CDMSFileChooser
from cdms_file_tree import CDMSFileTree
from manager import manager
from . import get_variables


class dummyVar(object):
    def __init__(self, id):
        self.id = id


class AddDialog(QtGui.QDialog):
    def __init__(self, parent=None, f=0):
        super(AddDialog, self).__init__(parent=parent, f=f)
        self.renameVar = None
        self.dialog = None
        self.reserved_words = ['and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or', 'with',
                               'assert', 'else', 'if', 'pass', 'yield', 'break', 'except', 'import', 'print', 'class',
                               'exec', 'in', 'raise', 'continue', 'finally', 'is', 'return', 'def', 'for', 'lambda',
                               'try']

        wrap = QtGui.QVBoxLayout()

        horiz = QtGui.QHBoxLayout()

        wrap.addLayout(horiz, 10)

        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                              QtGui.QDialogButtonBox.Cancel)
        import_button = QtGui.QPushButton("Import As")
        import_button.clicked.connect(self.rename_file)
        self.buttons.addButton(import_button, QtGui.QDialogButtonBox.ActionRole)
        self.buttons.accepted.connect(self.verify_selected_files)
        self.buttons.rejected.connect(self.reject)

        ok = self.buttons.button(QtGui.QDialogButtonBox.StandardButton.Ok)
        cancel = self.buttons.button(QtGui.QDialogButtonBox.StandardButton.Cancel)

        ok.setDefault(True)
        cancel.setDefault(False)

        wrap.addWidget(self.buttons)

        self.setLayout(wrap)

        self.tree = CDMSFileTree()
        tree_layout = QtGui.QVBoxLayout()
        toolbar = AddEditRemoveToolbar(u"Available Files",
                                       add_action=self.add_file,
                                       remove_action=self.remove_file)

        tree_layout.addWidget(toolbar, 0)
        tree_layout.addWidget(self.tree, 10)
        m = manager()
        for f in m.files:
            self.tree.add_file(m.files[f])

        m.addedFile.connect(self.addFileToTree)

        horiz.addLayout(tree_layout, 2)

        self.chooser = CDMSFileChooser()
        self.chooser.accepted.connect(self.added_files)

    def addFileToTree(self, file):
        self.tree.add_file(file)

    def selected_variables(self):
        if self.renameVar:
            var = self.renameVar
            self.renameVar = None
            return [var]
        else:
            return self.tree.get_selected()

    def add_file(self):
        self.chooser.show()  # pragma: no cover

    def added_files(self):
        files = self.chooser.get_selected()
        for cdmsfile in files:
            self.tree.add_file(cdmsfile)

    def remove_file(self):
        pass  # pragma: no cover

    def rename_file(self):
        var = self.tree.get_selected()
        if len(var) > 1:
            QtGui.QMessageBox.warning(self, "Error", "Please select one variable to import as")
            return
        var = var[0]

        while True:
            name = QtGui.QInputDialog.getText(self, u"Import As", u"Enter new variable name")
            if not name[1] or (name[1] and self.isValidName(name[0])):
                break

            QtGui.QMessageBox.warning(self, "Error", "Invalid name")

        str_name = name[0]
        var.id = str_name
        self.renameVar = var
        if name[1]:
            self.buttons.accepted.emit()
        else:
            self.buttons.rejected.emit()
        self.close()

    def isValidName(self, name):
        if name in self.reserved_words or not re.search("^[a-zA-Z_]", name) or name == '' \
                or re.search(' +', name) or re.search("[^a-zA-Z0-9_]+", name) \
                or get_variables().variable_exists(dummyVar(name)):
            return False
        return True

    def verify_selected_files(self):
        if not self.renameVar:
            vars = self.tree.get_selected()
            for var in vars:
                if not self.isValidName(var.id):
                    QtGui.QMessageBox.warning(self, "Error", "Invalid name for selected var(s)")
                    return
        self.accept()
