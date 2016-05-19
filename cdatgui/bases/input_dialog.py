from PySide import QtCore, QtGui


class AccessibleButtonDialog(QtGui.QWidget):
    accepted = QtCore.Signal()
    rejected = QtCore.Signal()

    def __init__(self):
        super(AccessibleButtonDialog, self).__init__()

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.cancel)

        self.save_button = QtGui.QPushButton('Save')
        self.save_button.clicked.connect(self.save)
        self.save_button.setEnabled(False)
        self.save_button.setDefault(True)
        self.cancel_button = QtGui.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.cancel)

        save_cancel_layout = QtGui.QHBoxLayout()
        save_cancel_layout.addWidget(self.cancel_button)
        save_cancel_layout.addWidget(self.save_button)

        self.vertical_layout = QtGui.QVBoxLayout()
        self.vertical_layout.addLayout(save_cancel_layout)

        self.setLayout(self.vertical_layout)

        self.setMaximumSize(300, 100)

    def cancel(self):
        self.close()
        self.rejected.emit()

    def save(self):
        self.close()
        self.accepted.emit()


class ValidatingInputDialog(AccessibleButtonDialog):
    def __init__(self):
        super(ValidatingInputDialog, self).__init__()

        self.label = QtGui.QLabel()
        self.edit = QtGui.QLineEdit()

        self.edit.returnPressed.connect(self.save_button.click)

        edit_line_layout = QtGui.QHBoxLayout()
        edit_line_layout.addWidget(self.label)
        edit_line_layout.addWidget(self.edit)

        self.vertical_layout.insertLayout(0, edit_line_layout)

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
