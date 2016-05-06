from PySide import QtGui, QtCore
from cdatgui.editors.template import TemplateEditor
import vcs
import copy
from cdatgui.bases.vcs_elements_dialog import VcsElementsDialog

from cdatgui.templates import get_templates


def sync_template(self, src):
    self.orientation = src.orientation
    self.file = copy.copy(src.file)
    self.function = copy.copy(src.function)
    self.logicalmask = copy.copy(src.logicalmask)
    self.transformation = copy.copy(src.transformation)
    self.source = copy.copy(src.source)
    self.dataname = copy.copy(src.dataname)
    self.title = copy.copy(src.title)
    self.units = copy.copy(src.units)
    self.crdate = copy.copy(src.crdate)
    self.crtime = copy.copy(src.crtime)
    self.comment1 = copy.copy(src.comment1)
    self.comment2 = copy.copy(src.comment2)
    self.comment3 = copy.copy(src.comment3)
    self.comment4 = copy.copy(src.comment4)
    self.xname = copy.copy(src.xname)
    self.yname = copy.copy(src.yname)
    self.zname = copy.copy(src.zname)
    self.tname = copy.copy(src.tname)
    self.xunits = copy.copy(src.xunits)
    self.yunits = copy.copy(src.yunits)
    self.zunits = copy.copy(src.zunits)
    self.tunits = copy.copy(src.tunits)
    self.xvalue = copy.copy(src.xvalue)
    self.yvalue = copy.copy(src.yvalue)
    self.zvalue = copy.copy(src.zvalue)
    self.tvalue = copy.copy(src.tvalue)
    self.mean = copy.copy(src.mean)
    self.min = copy.copy(src.min)
    self.max = copy.copy(src.max)
    self.xtic1 = copy.copy(src.xtic1)
    self.xtic2 = copy.copy(src.xtic2)
    self.xmintic1 = copy.copy(src.xmintic1)
    self.xmintic2 = copy.copy(src.xmintic2)
    self.ytic1 = copy.copy(src.ytic1)
    self.ytic2 = copy.copy(src.ytic2)
    self.ymintic1 = copy.copy(src.ymintic1)
    self.ymintic2 = copy.copy(src.ymintic2)
    self.xlabel1 = copy.copy(src.xlabel1)
    self.xlabel2 = copy.copy(src.xlabel2)
    self.ylabel1 = copy.copy(src.ylabel1)
    self.ylabel2 = copy.copy(src.ylabel2)
    self.box1 = copy.copy(src.box1)
    self.box2 = copy.copy(src.box2)
    self.box3 = copy.copy(src.box3)
    self.box4 = copy.copy(src.box4)
    self.line1 = copy.copy(src.line1)
    self.line2 = copy.copy(src.line2)
    self.line3 = copy.copy(src.line3)
    self.line4 = copy.copy(src.line4)
    self.legend = copy.copy(src.legend)
    self.data = copy.copy(src.data)


class TemplateEditorDialog(QtGui.QDialog):
    doneEditing = QtCore.Signal(str)

    def __init__(self, tmpl, parent=None):
        super(TemplateEditorDialog, self).__init__(parent=parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        shortcut.activated.connect(self.close)
        self.real_tmpl = tmpl
        self.tmpl = vcs.createtemplate(source=tmpl)
        l = QtGui.QVBoxLayout()
        self.editor = TemplateEditor()
        self.editor.setTemplate(self.tmpl)
        l.addWidget(self.editor)

        buttons = QtGui.QHBoxLayout()

        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save_as = QtGui.QPushButton("Save As")
        save_as.clicked.connect(self.customName)
        save = QtGui.QPushButton("Save")
        save.clicked.connect(self.accept)

        self.accepted.connect(self.save)
        save.setDefault(True)

        buttons.addWidget(cancel, alignment=QtCore.Qt.AlignLeft)
        buttons.addStretch()
        buttons.addWidget(save_as)
        buttons.addWidget(save)
        l.addLayout(buttons)

        self.setLayout(l)
        self.dialog = None

    def customName(self):
        # name = QtGui.QInputDialog.getText(self, u"Save As", u"Name for template:")
        self.dialog = VcsElementsDialog('template')
        self.dialog.setLabelText('Name:')
        self.dialog.setWindowTitle('Save As')

        self.dialog.accepted.connect(self.grabName)
        self.dialog.show()
        self.dialog.raise_()

    def grabName(self):
        self.save(self.dialog.textValue())

    def save(self, name=None):
        if name is None:
            sync_template(self.real_tmpl, self.tmpl)
            self.editTmpl(self.real_tmpl)
            name = self.real_tmpl.name
        else:
            if name in vcs.listelements('template'):
                del vcs.elements['template'][name]
            template = vcs.createtemplate(str(name), self.tmpl.name)
            self.makeTmpl(template)

        self.doneEditing.emit(name)
        self.close()

    def editTmpl(self, template):
        ind = get_templates().indexOf(template)
        if ind.isValid():
            get_templates().replace(ind.row(), template)

    def makeTmpl(self, template):
        get_templates().add_template(template)

