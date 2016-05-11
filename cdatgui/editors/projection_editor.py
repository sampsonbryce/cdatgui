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
        self.accepted.connect(self.savingNewProjection)
        self.editors = []
        self.auto_close = False
        self.newprojection_name = None

        self.proj_combo = QtGui.QComboBox()
        self.proj_combo.addItems(vcs.listelements('projection'))
        self.proj_combo.currentIndexChanged[str].connect(self.updateCurrentProjection)

        types = ["linear",
                 "utm",
                 "state plane",
                 "albers equal area",
                 "lambert conformal c",
                 "mercator",
                 "polar stereographic",
                 "polyconic",
                 "equid conic",
                 "transverse mercator",
                 "stereographic",
                 "lambert azimuthal",
                 "azimuthal",
                 "gnomonic",
                 "orthographic",
                 "gen. vert. near per",
                 "sinusoidal",
                 "equirectangular",
                 "miller cylindrical",
                 "van der grinten",
                 "hotin oblique merc",
                 "robinson",
                 "space oblique merc",
                 "alaska conformal",
                 "interrupted goode",
                 "mollweide",
                 "interrupt mollweide",
                 "hammer",
                 "wagner iv",
                 "wagner vii",
                 "oblated equal area"
                 ]

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

        well = QtGui.QFrame()
        well.setFrameShape(QtGui.QFrame.StyledPanel)
        well.setFrameShadow(QtGui.QFrame.Sunken)
        self.well_layout = QtGui.QVBoxLayout()
        well.setLayout(self.well_layout)
        self.well_layout.addLayout(type_row)

        self.vertical_layout.insertLayout(0, name_row)
        self.vertical_layout.insertWidget(1, well)

    def setProjectionObject(self, obj):
        self.orig_projection = obj
        self.cur_projection_name = obj.name
        self.object = vcs.createprojection(source=obj)
        self.newprojection_name = self.object.name

        self.updateAttributes()

    def updateAttributes(self):

        if self.cur_projection_name == 'default':
            self.save_button.setEnabled(False)
        else:
            self.save_button.setEnabled(True)

        for i in range(1, self.well_layout.count()):
            row = self.well_layout.takeAt(1).layout()
            row.takeAt(0).widget().deleteLater()
            row.takeAt(0).widget().deleteLater()
            row.deleteLater()
        self.editors = []

        # set name
        block = self.proj_combo.blockSignals(True)
        self.proj_combo.setCurrentIndex(self.proj_combo.findText(self.cur_projection_name))
        self.proj_combo.blockSignals(block)

        # set type
        block = self.type_combo.blockSignals(True)
        self.type_combo.setCurrentIndex(self.type_combo.findText(self.object.type))
        self.type_combo.blockSignals(block)

        for name in self.object.attributes:
            value = getattr(self.object, name)

            edit_attr = QtGui.QLineEdit()
            edit_attr.setText(str(value))
            self.editors.append((edit_attr, name))

            row = QtGui.QHBoxLayout()
            row.addWidget(label(name.capitalize() + ":"))
            row.addWidget(edit_attr)

            # self.vertical_layout.insertLayout(self.vertical_layout.count() - 1, row)
            self.well_layout.addLayout(row)

    def updateCurrentProjection(self, proj):
        proj = str(proj)
        self.cur_projection_name = proj
        if self.newprojection_name in vcs.listelements('projection'):
            del vcs.elements['projection'][self.newprojection_name]
        self.object = vcs.createprojection(source=vcs.getprojection(proj))
        self.newprojection_name = self.object.name
        self.updateAttributes()

    def updateProjectionType(self, type):
        self.object.type = str(type)
        self.updateAttributes()

    def updateProjection(self):
        for editor, attr in self.editors:
            if isinstance(editor, QtGui.QComboBox):
                text = editor.currentText()
            else:
                text = editor.text()
            try:
                text = float(text)
            except ValueError:
                QtGui.QMessageBox.critical(self, "Invalid Type",
                                           "Value '{0}' for {1} is not valid.".format(text, attr.capitalize()))
                return False

            setattr(self.object, attr, text)
        return True

    def savingNewProjection(self, name):
        if not self.updateProjection():
            return

        if name == self.newprojection_name:
            del vcs.elements['projection'][self.cur_projection_name]
            vcs.createprojection(self.cur_projection_name, self.object)
            name = self.cur_projection_name
        else:
            if name in vcs.listelements('projection'):
                del vcs.elements['projection'][name]
            vcs.createprojection(name, vcs.elements['projection'][self.newprojection_name])

        self.gm.projection = name
        self.close()

    def close(self):
        if self.newprojection_name in vcs.elements['projection']:
            del vcs.elements['projection'][self.newprojection_name]
        super(ProjectionEditor, self).close()
