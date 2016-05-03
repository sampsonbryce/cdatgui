from PySide import QtGui, QtCore

import re
from functools import partial

from cdatgui.toolbars import AddEditRemoveToolbar
from cdms_file_chooser import CDMSFileChooser
from cdms_file_tree import CDMSFileTree
from manager import manager
from . import get_variables, reserved_words
from cdatgui.bases.input_dialog import ValidatingInputDialog


class dummyVar(object):
    def __init__(self, id):
        self.id = id


class FileNameValidator(QtGui.QValidator):
    invalidInput = QtCore.Signal()
    validInput = QtCore.Signal()

    def __init__(self):
        super(FileNameValidator, self).__init__()

    def validate(self, name, pos):
        if name in reserved_words() or not re.search("^[a-zA-Z_]", name) or name == '' \
                or re.search(' +', name) or re.search("[^a-zA-Z0-9_]+", name) \
                or get_variables().variable_exists(dummyVar(name)):
            self.invalidInput.emit()
            return QtGui.QValidator.Intermediate
        self.validInput.emit()
        return QtGui.QValidator.Acceptable


class AddDialog(QtGui.QDialog):
    def __init__(self, parent=None, f=0):
        super(AddDialog, self).__init__(parent=parent, f=f)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.renameVar = []
        self.dialog = None

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
            var_list = self.renameVar
            self.renameVar = []
            return var_list
        else:
            return self.tree.get_selected()

    def add_file(self):
        self.chooser.show()  # pragma: no cover

    def added_files(self):
        files = self.chooser.get_selected()
        for cdmsfile in files:
            self.tree.add_file(cdmsfile)

    def remove_file(self):
        sel = self.tree.selectedItems()
        for item in sel:
            i = item.parent().takeChild(item.parent().indexOfChild(item))
            del i

        file_count = self.tree.topLevelItemCount()
        i = 0
        while i < file_count:
            if not self.tree.topLevelItem(i).childCount():
                file = self.tree.takeTopLevelItem(i)
                manager().remove_file(file)
                del file
                file_count -= 1
            else:
                i += 1

    def rename_file(self):
        var = self.tree.get_selected()
        if len(var) > 1 or len(var) < 1:
            QtGui.QMessageBox.warning(self, "Error", "Please select one variable to import as")
            return
        var = var[0]

        self.dialog = ValidatingInputDialog()
        self.dialog.setValidator(FileNameValidator())
        self.dialog.accepted.connect(partial(self.setRenameVar, var))
        self.dialog.setWindowTitle("Import As")
        self.dialog.setLabelText("Enter New Name:")

        self.dialog.show()
        self.dialog.raise_()

    def setRenameVar(self, var):
        self.renameVar.append(var)
        self.renameVar[-1].id = self.dialog.textValue()
        self.accepted.emit()
        self.dialog.close()
        self.tree.clearSelection()

    def isValidName(self, name):
        if name in reserved_words() or not re.search("^[a-zA-Z_]", name) or name == '' \
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
