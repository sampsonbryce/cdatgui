from PySide import QtCore, QtGui


class BaseSaveWindowWidget(QtGui.QWidget):
    accepted = QtCore.Signal(str)
    rejected = QtCore.Signal()

    def __init__(self, parent=None):
        super(BaseSaveWindowWidget, self).__init__()
        self.auto_close = True
        self.object = None
        self.preview = None
        self.dialog = QtGui.QInputDialog()
        self.dialog.setModal(QtCore.Qt.ApplicationModal)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.reject)

        # Layout to add new elements
        self.vertical_layout = QtGui.QVBoxLayout()

        # Save and Cancel Buttons
        cancel_button = QtGui.QPushButton()
        cancel_button.setText("Cancel")
        cancel_button.clicked.connect(self.reject)

        saveas_button = QtGui.QPushButton()
        saveas_button.setText("Save As")
        saveas_button.clicked.connect(self.saveAs)

        self.save_button = QtGui.QPushButton()
        self.save_button.setText("Save")
        self.save_button.clicked.connect(self.accept)

        save_cancel_row = QtGui.QHBoxLayout()
        save_cancel_row.addWidget(cancel_button)
        save_cancel_row.addWidget(saveas_button)
        save_cancel_row.addWidget(self.save_button)
        save_cancel_row.insertStretch(1, 1)

        # Set up vertical_layout
        self.vertical_layout.addLayout(save_cancel_row)
        self.setLayout(self.vertical_layout)

    def setPreview(self, preview):
        if self.preview:
            self.vertical_layout.removeWidget(self.preview)
            self.preview.deleteLater()

        self.preview = preview
        self.vertical_layout.insertWidget(0, self.preview)

    def saveAs(self):

        self.win = self.dialog

        self.win.setLabelText("Enter New Name:")
        self.win.accepted.connect(self.accept)

        self.win.show()
        self.win.raise_()

    def accept(self):

        try:
            name = self.win.textValue()
            self.win.close()
            self.win.deleteLater()
        except:
            name = self.object.name

        self.accepted.emit(name)
        if self.auto_close:
            self.close()

    def setSaveDialog(self, dialog):
        self.dialog = dialog

    def reject(self):
        self.rejected.emit()
        self.close()


class BaseOkWindowWidget(QtGui.QWidget):
    accepted = QtCore.Signal()
    rejected = QtCore.Signal()

    def __init__(self, parent=None):
        super(BaseOkWindowWidget, self).__init__()

        self.object = None
        self.preview = None
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.reject)

        # Layout to add new elements
        self.vertical_layout = QtGui.QVBoxLayout()

        # Save and Cancel Buttons
        cancel_button = QtGui.QPushButton()
        cancel_button.setText("Cancel")
        cancel_button.clicked.connect(self.reject)

        ok_button = QtGui.QPushButton()
        ok_button.setText("OK")
        ok_button.clicked.connect(self.accept)

        ok_cancel_row = QtGui.QHBoxLayout()
        ok_cancel_row.addWidget(cancel_button)
        ok_cancel_row.addWidget(ok_button)
        ok_cancel_row.insertStretch(1, 1)

        # Set up vertical_layout
        self.vertical_layout.addLayout(ok_cancel_row)
        self.setLayout(self.vertical_layout)

    def setPreview(self, preview):
        if self.preview:
            self.vertical_layout.removeWidget(self.preview)
            self.preview.deleteLater()

        self.preview = preview
        self.vertical_layout.insertWidget(0, self.preview)

    def accept(self):
        self.accepted.emit()
        self.close()

    def reject(self):
        self.rejected.emit()
        self.close()
