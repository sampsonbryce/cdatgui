from PySide import QtGui, QtCore
from cdatgui.editors.boxfill import BoxfillEditor
import vcs


class BoxfillDialog(QtGui.QDialog):
    editedGM = QtCore.Signal(object)
    createdGM = QtCore.Signal(object)

    def __init__(self, gm, var, tmpl, parent=None):
        super(BoxfillDialog, self).__init__(parent=parent)
        layout = QtGui.QVBoxLayout()
        self.gm = gm
        self.editor = BoxfillEditor()
        self.editor.gm = gm
        self.editor.var = var
        self.editor.tmpl = tmpl
        layout.addWidget(self.editor)

        buttons = QtGui.QHBoxLayout()
        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save_as = QtGui.QPushButton("Save As")
        save_as.clicked.connect(self.customName)
        save = QtGui.QPushButton("Save")
        save.clicked.connect(self.accept)

        self.accepted.connect(self.save)
        save.setDefault(True)

        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(save_as)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def customName(self):
        name = QtGui.QInputDialog.getText(self, u"Save As", u"Name for Boxfill:")
        self.save(name)

    def save(self, name=None):
        if name is None:
            self.editedGM.emit(self.gm)
        else:
            gm = vcs.createboxfill(name, self.gm)
            self.createdGM.emit(gm)
