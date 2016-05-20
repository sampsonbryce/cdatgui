from PySide import QtCore, QtGui


class AccessibleButtonDialog(QtGui.QWidget):
    accepted = QtCore.Signal()
    rejected = QtCore.Signal()

    def __init__(self, parent=None):
        super(AccessibleButtonDialog, self).__init__(parent=parent)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.reject)

        self.save_button = QtGui.QPushButton('Save')
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        self.cancel_button = QtGui.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)

        save_cancel_layout = QtGui.QHBoxLayout()
        save_cancel_layout.addWidget(self.cancel_button)
        save_cancel_layout.addWidget(self.save_button)

        self.vertical_layout = QtGui.QVBoxLayout()
        self.vertical_layout.addLayout(save_cancel_layout)

        self.setLayout(self.vertical_layout)

        self.setMaximumSize(300, 100)

    def reject(self):
        self.close()
        self.rejected.emit()

    def accept(self):
        self.close()
        self.accepted.emit()


class ValidatingInputDialog(AccessibleButtonDialog):
    def __init__(self, parent=None):
        super(ValidatingInputDialog, self).__init__(parent=parent)

        self.label = QtGui.QLabel()
        self.edit = QtGui.QLineEdit()

        self.edit.returnPressed.connect(self.save_button.click)

        edit_line_layout = QtGui.QHBoxLayout()
        edit_line_layout.addWidget(self.label)
        edit_line_layout.addWidget(self.edit)

        self.vertical_layout.insertLayout(0, edit_line_layout)

        self.save_button.setEnabled(False)
        self.edit.setFocus()

    def setLabelText(self, text):
        self.label.setText(text)

    def setValidator(self, validator):
        self.edit.setValidator(validator)

        try:
            validator.invalidInput.connect(lambda: self.save_button.setEnabled(False))
            validator.validInput.connect(lambda: self.save_button.setEnabled(True))
        except AttributeError:
            pass

    def textValue(self):
        return self.edit.text().strip()

    def setTextValue(self, text):
        self.edit.setText(text)
