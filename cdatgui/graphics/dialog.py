from PySide import QtGui, QtCore

from cdatgui.bases.vcs_elements_dialog import VcsElementsDialog
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
        self.origgm_name = gm.name

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
        self.gm = self.createNewGM(gm)
        self.newgm_name = self.gm.name
        self.editor.gm = self.gm

        self.setWindowTitle('Editing ' + gm.name)

        layout.addWidget(self.editor)

        self.buttons = QtGui.QHBoxLayout()
        cancel = QtGui.QPushButton("Cancel")
        cancel.setAutoDefault(True)
        cancel.clicked.connect(self.reject)

        self.buttons.addWidget(cancel)
        self.buttons.addStretch()

        layout.addLayout(self.buttons)

        self.setLayout(layout)

    def createNewGM(self, gm):
        """This is here so it can be overridden when inherited"""
        return self.create(source=gm)

    def reject(self):
        super(GraphicsMethodDialog, self).reject()

        if isinstance(self.editor, BoxfillEditor):
            self.gm.boxfill_type = self.editor.orig_type

        if self.newgm_name in vcs.elements[vcs.graphicsmethodtype(self.gm)].keys():
            del vcs.elements[vcs.graphicsmethodtype(self.gm)][self.newgm_name]


class GraphicsMethodSaveDialog(GraphicsMethodDialog):
    def __init__(self, gm, var, tmpl, parent=None):
        super(GraphicsMethodSaveDialog, self).__init__(gm, var, tmpl, parent)
        self.dialog = None

        save_as = QtGui.QPushButton("Save As")
        save_as.clicked.connect(self.customName)
        save = QtGui.QPushButton("Save")
        save.setDefault(True)
        save.clicked.connect(self.accept)

        self.buttons.addWidget(save_as)
        self.buttons.addWidget(save)

        self.accepted.connect(self.save)

        if self.origgm_name == 'default':
            save.setEnabled(False)

    def customName(self):
        self.dialog = VcsElementsDialog('boxfill')
        self.dialog.setLabelText('Name for {0}'.format(unicode(self.gmtype)))
        self.dialog.setWindowTitle('Save As')
        self.dialog.accepted.connect(self.grabGm)
        self.dialog.show()
        self.dialog.raise_()

    def grabGm(self):
        self.save(self.dialog.textValue())

    def save(self, name=None):
        if name is None:
            del vcs.elements[self.gmtype][self.origgm_name]
            gm = vcs.creategraphicsmethod(self.gmtype, self.newgm_name, self.origgm_name)
            self.editedGM.emit(gm)
        else:
            if name in vcs.listelements(self.gmtype):
                del vcs.elements[self.gmtype][name]
            gm = self.create(name, self.newgm_name)
            self.createdGM.emit(gm)

        del vcs.elements[self.gmtype][self.newgm_name]

        self.close()


class GraphicsMethodOkDialog(GraphicsMethodDialog):
    def __init__(self, gm, var, tmpl, parent=None):
        super(GraphicsMethodOkDialog, self).__init__(gm, var, tmpl, parent)

        ok_button = QtGui.QPushButton('OK')
        ok_button.clicked.connect(self.accept)

        self.accepted.connect(self.okClicked)
        self.buttons.addWidget(ok_button)

    def okClicked(self):
        del vcs.elements[self.gmtype][self.origgm_name]
        gm = vcs.creategraphicsmethod(self.gmtype, self.newgm_name, self.origgm_name)
        self.editedGM.emit(gm)
        del vcs.elements[self.gmtype][self.newgm_name]
