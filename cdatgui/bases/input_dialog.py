from PySide import QtCore, QtGui


class ValidatingInputDialog(QtGui.QWidget):
    accepted = QtCore.Signal()
    rejected = QtCore.Signal()

    def __init__(self):
        super(ValidatingInputDialog, self).__init__()

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.cancel)

        vertical_layout = QtGui.QVBoxLayout()

        self.label = QtGui.QLabel()
        self.edit = QtGui.QLineEdit()

        self.save_button = QtGui.QPushButton('Save')
        self.save_button.clicked.connect(self.save)
        self.save_button.setEnabled(False)
        self.save_button.setDefault(True)
        cancel_button = QtGui.QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)

        self.edit.returnPressed.connect(self.save_button.click)

        edit_line_layout = QtGui.QHBoxLayout()
        edit_line_layout.addWidget(self.label)
        edit_line_layout.addWidget(self.edit)

        save_cancel_layout = QtGui.QHBoxLayout()
        save_cancel_layout.addWidget(cancel_button)
        save_cancel_layout.addWidget(self.save_button)

        vertical_layout.addLayout(edit_line_layout)
        vertical_layout.addLayout(save_cancel_layout)

        self.setLayout(vertical_layout)

        self.setMaximumSize(300, 100)

    def cancel(self):
        self.close()
        self.rejected.emit()

    def save(self):
        self.close()
        self.accepted.emit()

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
