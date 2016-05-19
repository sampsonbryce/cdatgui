from cdatgui.bases.input_dialog import ValidatingInputDialog
from PySide import QtCore, QtGui
import vcs


class VCSElementsDialog(ValidatingInputDialog):
    def __init__(self, element):
        super(VCSElementsDialog, self).__init__()
        self.element = element
        self.setValidator(VCSElementsValidator())

    def save(self):
        if self.textValue() in vcs.elements[self.element] or self.textValue() + '_miniticks' in vcs.elements[self.element]:
            check = QtGui.QMessageBox.question(self, "Overwrite {0}?".format(self.element),
                                               "{0} '{1}' already exists. Overwrite?".format(self.element.capitalize(), self.textValue()),
                                               buttons=QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
            if check == QtGui.QDialogButtonBox.FirstButton:
                self.close()
                self.accepted.emit()
        else:
            self.close()
            self.accepted.emit()


class VCSElementsValidator(QtGui.QValidator):
    invalidInput = QtCore.Signal()
    validInput = QtCore.Signal()

    def validate(self, inp, pos):
        inp = inp.strip()
        if not inp or inp == 'default':
            self.invalidInput.emit()
            return QtGui.QValidator.Intermediate

        self.validInput.emit()
        return QtGui.QValidator.Acceptable
