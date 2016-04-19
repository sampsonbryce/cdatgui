from PySide import QtGui, QtCore
from cdatgui.editors.boxfill import BoxfillEditor
from cdatgui.editors.isofill import IsofillEditor
from cdatgui.editors.meshfill import MeshfillEditor
from cdatgui.editors.isoline import IsolineEditor
from cdatgui.editors.cdat1d import Cdat1dEditor
from cdatgui.editors.vector import VectorEditor
import vcs


class GraphcisMethodDialog(QtGui.QDialog):
    editedGM = QtCore.Signal(object)
    createdGM = QtCore.Signal(object)

    def __init__(self, gm, var, tmpl, parent=None):
        super(GraphcisMethodDialog, self).__init__(parent=parent)

        layout = QtGui.QVBoxLayout()

        self.gmtype = vcs.graphicsmethodtype(gm)
        if self.gmtype == "boxfill":
            self.editor = BoxfillEditor()
            self.editor.type_group.checkedButton().clicked.emit()
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
        layout.addWidget(self.editor)

        buttons = QtGui.QHBoxLayout()
        cancel = QtGui.QPushButton("Cancel")
        cancel.setAutoDefault(True)
        cancel.clicked.connect(self.reject)
        save_as = QtGui.QPushButton("Save As")
        save_as.clicked.connect(self.customName)
        save = QtGui.QPushButton("Save")
        save.setDefault(True)
        save.clicked.connect(self.accept)

        self.accepted.connect(self.save)

        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(save_as)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        self.setLayout(layout)

        print "GM NAME", gm.name
        if gm.name == 'default':
            self.gm = self.create('new', gm)
            save.setEnabled(False)
        else:
            self.gm = gm

        self.editor.gm = self.gm

    def updateGM(self, gm):
        self.gm = gm

    def customName(self):
        name = QtGui.QInputDialog.getText(self, u"Save As", u"Name for {0}:".format(unicode(self.gmtype)))
        if name[1]:
            self.save(name)

    def save(self, name=None):
        if name is None:
            self.editedGM.emit(self.gm)
        else:
            gm = self.create(name[0], self.gm)
            self.close()
            self.createdGM.emit(gm)

    def reject(self):
        super(GraphcisMethodDialog, self).reject()
        if 'new' in vcs.elements[vcs.graphicsmethodtype(self.gm)].keys():
            del vcs.elements[vcs.graphicsmethodtype(self.gm)]['new']
