from PySide import QtGui, QtCore
from cdatgui.editors.boxfill import BoxfillEditor
from cdatgui.editors.isofill import IsofillEditor
from cdatgui.editors.meshfill import MeshfillEditor
from cdatgui.editors.isoline import IsolineEditor
from cdatgui.editors.cdat1d import Cdat1dEditor
from cdatgui.editors.vector import VectorEditor
import vcs


class GraphicsMethodDialog(QtGui.QDialog):
    editedGM = QtCore.Signal(object)
    createdGM = QtCore.Signal(object)

    def __init__(self, gm, var, tmpl, parent=None):
        super(GraphicsMethodDialog, self).__init__(parent=parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.newgm_name = None

        layout = QtGui.QVBoxLayout()

        self.gmtype = vcs.graphicsmethodtype(gm)
        if self.gmtype == "boxfill":
            self.editor = BoxfillEditor()
            self.create = vcs.createboxfill
        elif self.gmtype == "isofill":
            self.editor = IsofillEditor()
            self.create = vcs.createisofill
        elif self.gmtype == "meshfill":
            self.editor = MeshfillEditor()
            self.create = vcs.createmeshfill
        elif self.gmtype == "isoline":
            self.editor = IsolineEditor()
            self.create = vcs.createisoline
        elif self.gmtype == "1d":
            self.editor = Cdat1dEditor()
            self.create = vcs.create1d
        elif self.gmtype == "vector":
            self.editor = VectorEditor()
            self.create = vcs.createvector
        else:
            raise NotImplementedError("No editor exists for type %s" % self.gmtype)
        self.editor.var = var
        self.editor.tmpl = tmpl
        self.gm = gm
        self.editor.gm = gm

        layout.addWidget(self.editor)

        self.buttons = QtGui.QHBoxLayout()
        cancel = QtGui.QPushButton("Cancel")
        cancel.setAutoDefault(True)
        cancel.clicked.connect(self.reject)

        self.buttons.addWidget(cancel)
        self.buttons.addStretch()

        layout.addLayout(self.buttons)

        self.setLayout(layout)

    def reject(self):
        super(GraphicsMethodDialog, self).reject()
        if isinstance(self.editor, BoxfillEditor):
            self.gm.boxfill_type = self.editor.orig_type

        if self.newgm_name in vcs.elements[vcs.graphicsmethodtype(self.gm)].keys():
            del vcs.elements[vcs.graphicsmethodtype(self.gm)][self.newgm_name]


class GraphicsMethodSaveDialog(GraphicsMethodDialog):
    def __init__(self, gm, var, tmpl, parent=None):
        super(GraphicsMethodSaveDialog, self).__init__(gm, var, tmpl, parent)

        save_as = QtGui.QPushButton("Save As")
        save_as.clicked.connect(self.customName)
        save = QtGui.QPushButton("Save")
        save.setDefault(True)
        save.clicked.connect(self.accept)

        self.buttons.addWidget(save_as)
        self.buttons.addWidget(save)

        self.accepted.connect(self.save)
        if gm.name == 'default':
            self.gm = self.create(source=gm)
            self.newgm_name = self.gm.name
            save.setEnabled(False)
        else:
            self.gm = gm

        self.editor.gm = self.gm

    def customName(self):
        name = QtGui.QInputDialog.getText(self, u"Save As", u"Name for {0}:".format(unicode(self.gmtype)))
        if name[1]:
            self.save(name)

    def save(self, name=None):
        if name is None:
            self.editedGM.emit(self.gm)
        else:
            gm = self.create(name[0], self.gm)
            self.createdGM.emit(gm)

        self.close()


class GraphicsMethodOkDialog(GraphicsMethodDialog):
    def __init__(self, gm, var, tmpl, parent=None):
        super(GraphicsMethodOkDialog, self).__init__(gm, var, tmpl, parent)

        ok_button = QtGui.QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        self.buttons.addWidget(ok_button)

