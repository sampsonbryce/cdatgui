from PySide import QtCore, QtGui
import vcs, sys
from cdatgui.bases.window_widget import BaseSaveWindowWidget
from cStringIO import StringIO
from cdatgui.utils import label
from cdatgui.bases.vcs_elements_dialog import VcsElementsDialog, VcsElementsValidator


class ProjectionEditor(BaseSaveWindowWidget):
    def __init__(self):
        super(ProjectionEditor, self).__init__()
        dialog = VcsElementsDialog('projection')
        dialog.setValidator(VcsElementsValidator())
        self.setSaveDialog(dialog)
        self.orig_projection = None
        self.cur_projection_name = None
        self.gm = None
        self.savePressed.connect(self.savingNewProjection)
        self.editors = []

        self.proj_combo = QtGui.QComboBox()
        self.proj_combo.addItems(vcs.listelements('projection'))
        self.proj_combo.currentIndexChanged[str].connect(self.updateCurrentProjection)

        types = ["linear",
                 "utm",
                 "state plane",
                 "albers equal area", "albers",
                 "lambert",
                 "lambert conformal c",
                 "lambert conformal conic",
                 "mercator",
                 "polar",
                 "polar stereographic",
                 "polyconic",
                 "equid conic a",
                 "equid conic",
                 "equid conic b",
                 "transverse mercator",
                 "stereographic",
                 "lambert azimuthal",
                 "azimuthal",
                 "gnomonic",
                 "orthographic",
                 "gen. vert. near per",
                 "gen vert near per",
                 "sinusoidal",
                 "equirectangular",
                 "miller",
                 "miller cylindrical",
                 "van der grinten",
                 "hotin",
                 "hotin oblique",
                 "hotin oblique merc",
                 "hotin oblique merc a",
                 "hotin oblique merc b",
                 "hotin oblique mercator",
                 "hotin oblique mercator a",
                 "hotin oblique mercator b",
                 "robinson",
                 "space oblique",
                 "space oblique merc",
                 "space oblique merc a",
                 "space oblique merc b",
                 "alaska", "alaska conformal",
                 "interrupted goode", "goode",
                 "mollweide",
                 "interrupted mollweide",
                 "interrupt mollweide",
                 "hammer",
                 "wagner iv",
                 "wagner 4",
                 "wagner4",
                 "wagner vii",
                 "wagner 7",
                 "wagner7",
                 "oblated",
                 "oblated equal area"]
        self.type_combo = QtGui.QComboBox()
        self.type_combo.addItems(types)
        self.type_combo.currentIndexChanged[str].connect(self.updateProjectionType)

        name_label = label("Select Projection:")
        type_label = label("Type:")

        name_row = QtGui.QHBoxLayout()
        name_row.addWidget(name_label)
        name_row.addWidget(self.proj_combo)

        type_row = QtGui.QHBoxLayout()
        type_row.addWidget(type_label)
        type_row.addWidget(self.type_combo)

        self.vertical_layout.insertLayout(0, name_row)
        self.vertical_layout.insertLayout(1, type_row)

    def setProjectionObject(self, obj):
        if obj.name == 'default':
            self.save_button.setEnabled(False)
        self.orig_projection = obj
        self.cur_projection_name = obj.name
        self.object = vcs.createprojection('new', obj)
        self.updateAttributes()

    def updateAttributes(self):
        obj = self.object

        for i in range(2, self.vertical_layout.count() - 1):
            row = self.vertical_layout.takeAt(2).layout()
            row.takeAt(0).widget().deleteLater()
            row.takeAt(0).widget().deleteLater()
            row.deleteLater()
        self.editors = []

        orig_out = sys.stdout
        sys.stdout = myout = StringIO()
        obj.list()
        sys.stdout = orig_out
        lst = myout.getvalue().split('\n')
        print 'LIST', lst
        for item in lst[2:-1]:
            left, right = item.split('=')
            left = left.strip()
            right = right.strip()

            if left == 'name':
                block = self.proj_combo.blockSignals(True)
                self.proj_combo.setCurrentIndex(self.proj_combo.findText(self.cur_projection_name))
                self.proj_combo.blockSignals(block)
                continue
            if left == 'type':
                block = self.type_combo.blockSignals(True)
                self.type_combo.setCurrentIndex(self.type_combo.findText(right))
                self.type_combo.blockSignals(block)
                continue

            edit_attr = QtGui.QLineEdit()
            edit_attr.setText(right)
            self.editors.append((edit_attr, left))

            row = QtGui.QHBoxLayout()
            row.addWidget(label(left.capitalize() + ":"))
            row.addWidget(edit_attr)

            self.vertical_layout.insertLayout(self.vertical_layout.count() - 1, row)

    def updateCurrentProjection(self, proj):
        proj = str(proj)
        self.cur_projection_name = proj
        if 'new' in vcs.listelements('projection'):
            del vcs.elements['projection']['new']
        vcs.getprojection(proj).list()
        self.object = vcs.createprojection('new', vcs.getprojection(proj))
        self.updateAttributes()

    def updateProjectionType(self, type):
        self.object.type = str(type)
        self.updateAttributes()

    def savingNewProjection(self, name):
        if name == 'new':
            vcs.elements['projection'].pop(self.cur_projection_name)
            vcs.createprojection(self.cur_projection_name, self.object)
            name = self.cur_projection_name
        else:
            vcs.createprojection(name, vcs.elements['projection']['new'])

        new = vcs.elements['projection'].pop('new')
        del new

        self.gm.projection = name

    def close(self):
        if 'new' in vcs.elements['projection']:
            new = vcs.elements['projection'].pop('new')
            del new
        super(ProjectionEditor, self).close()
