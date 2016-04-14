from PySide import QtGui, QtCore
from cdatgui.editors.boxfill import BoxfillEditor
from cdatgui.editors.isofill import IsofillEditor
import vcs


class GraphcisMethodDialog(QtGui.QDialog):
    editedGM = QtCore.Signal(object)
    createdGM = QtCore.Signal(object)

    def __init__(self, gm, var, tmpl, parent=None):
        super(GraphcisMethodDialog, self).__init__(parent=parent)
        # self.graphics_methods = ['boxfill', 'isofill', 'isoline', 'meshfill', '3d_scalar', '3d_dual_scalar',

        layout = QtGui.QVBoxLayout()
        self.gm = gm
        self.editor = eval('{0}Editor()'.format(vcs.graphicsmethodtype(self.gm).capitalize()))
        # self.editor = BoxfillEditor()
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
            # gm = vcs.createboxfill(name, self.gm)
            gm = eval('vcs.create{0}(name, self.gm)'.format(vcs.graphicsmethodtype(self.gm)))
            self.createdGM.emit(gm)
