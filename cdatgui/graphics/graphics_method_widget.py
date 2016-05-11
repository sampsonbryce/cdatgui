import copy
from PySide import QtCore, QtGui
from cdatgui.bases import StaticDockWidget
from cdatgui.toolbars import AddEditRemoveToolbar
from vcs_gm_list import GraphicsMethodList
from cdatgui.bases.input_dialog import ValidatingInputDialog
from cdatgui.graphics import get_gms
from cdatgui.graphics.dialog import GraphicsMethodOkDialog
from cdatgui.utils import label
from cdatgui.cdat.metadata import FileMetadataWrapper
from . import gms_with_non_implemented_editors
import vcs, cdms2, os


class NameValidator(QtGui.QValidator):
    invalidInput = QtCore.Signal()
    validInput = QtCore.Signal()

    def __init__(self):
        super(NameValidator, self).__init__()
        self.gm_type = None

    def validate(self, inp, pos):
        if not self.gm_type:
            raise Exception("Must set gm_type")
        if not inp or inp in vcs.listelements(self.gm_type):
            self.invalidInput.emit()
            return QtGui.QValidator.Intermediate
        else:
            self.validInput.emit()
            return QtGui.QValidator.Acceptable


class EditGmDialog(GraphicsMethodOkDialog):
    def __init__(self, gtype, ginstance, store=True):
        """Store designates whether the gm is to be saved on okPressed for use when creating new gms"""
        self.gtype = gtype
        self.ginstance = ginstance
        f = cdms2.open(os.path.join(vcs.sample_data, 'clt.nc'))
        f = FileMetadataWrapper(f)
        var = f('clt')

        gm = vcs.creategraphicsmethod(str(gtype), str(ginstance))
        tmpl = vcs.createtemplate()

        self.edit_tmpl_name = tmpl.name
        self.edit_gm_name = gm.name
        super(EditGmDialog, self).__init__(gm, var, tmpl)

        self.setWindowTitle('Editing ' + self.ginstance)

        self.rejected.connect(self.resetGM)
        self.rejected.connect(self.resetTmpl)

        if not store:
            self.accepted.connect(self.createGM)

    def createNewGM(self, gm):
        return gm

    def okClicked(self):
        self.hide()

    def resetGM(self):
        if self.edit_gm_name:
            del vcs.elements[self.gtype][self.edit_gm_name]
        self.edit_gm_name = None

    def resetTmpl(self):
        if self.edit_tmpl_name:
            del vcs.elements['template'][self.edit_tmpl_name]
        self.edit_tmpl_name = None

    def createGM(self):
        cur_index = get_gms().indexOf(self.gtype, vcs.getgraphicsmethod(self.gtype, self.ginstance))
        del vcs.elements[self.gtype][self.ginstance]
        if self.edit_gm_name:
            gm = vcs.creategraphicsmethod(self.gtype, self.edit_gm_name, self.ginstance)
            get_gms().replace(cur_index, gm)
        self.resetTmpl()
        self.resetGM()


class CreateGM(ValidatingInputDialog):
    def __init__(self, currently_selected, parent=None):
        super(CreateGM, self).__init__()

        self.edit_dialog = None

        validator = NameValidator()
        self.setValidator(validator)
        self.setLabelText('Name:')

        self.gm_type_combo = QtGui.QComboBox()
        self.gm_type_combo.setModel(get_gms())
        if currently_selected:
            self.gm_type_combo.setCurrentIndex(self.gm_type_combo.findText(currently_selected[0]))
        self.gm_type_combo.currentIndexChanged.connect(self.setGMRoot)
        self.edit.validator().gm_type = self.gm_type_combo.currentText()

        # Create the instance combo first so the setGMRoot function can update it properly
        self.gm_instance_combo = QtGui.QComboBox()
        self.gm_instance_combo.setModel(get_gms())
        self.gm_instance_combo.setRootModelIndex(get_gms().index(self.gm_type_combo.currentIndex(), 0))
        if currently_selected and len(currently_selected) > 1:
            self.gm_instance_combo.setCurrentIndex(self.gm_instance_combo.findText(currently_selected[1]))
        else:
            self.gm_instance_combo.setCurrentIndex(self.gm_instance_combo.findText('default'))

        type_layout = QtGui.QHBoxLayout()
        type_layout.addWidget(label('Graphics Method Type:'))
        type_layout.addWidget(self.gm_type_combo)

        instance_layout = QtGui.QHBoxLayout()
        instance_layout.addWidget(label('Graphics Method:'))
        instance_layout.addWidget(self.gm_instance_combo)

        self.vertical_layout.insertLayout(0, instance_layout)
        self.vertical_layout.insertLayout(0, type_layout)

        # add customize button
        if not (currently_selected and currently_selected[0] in gms_with_non_implemented_editors):
            button_layout = self.vertical_layout.itemAt(self.vertical_layout.count() - 1).layout()
            customize_button = QtGui.QPushButton('Customize')
            customize_button.clicked.connect(self.editGM)
            button_layout.insertWidget(1, customize_button)

        self.accepted.connect(self.createGM)

    def setGMRoot(self, index):
        if self.edit_dialog is not None:
            self.edit_dialog.deleteLater()
            self.edit_dialog = None
        self.edit.validator().gm_type = self.gm_type_combo.currentText()
        self.gm_instance_combo.setRootModelIndex(get_gms().index(index, 0))
        self.gm_instance_combo.setCurrentIndex(self.gm_instance_combo.findText('default'))
        self.edit.validator().validate(self.edit.text(), 0)

    def createGM(self):
        if self.edit_dialog and self.edit_dialog.edit_gm_name:
            gm = vcs.creategraphicsmethod(str(self.gm_type_combo.currentText()),
                                         self.edit_dialog.edit_gm_name,
                                         str(self.textValue()))
            get_gms().add_gm(gm)
            del vcs.elements[self.gm_type_combo.currentText()][self.edit_dialog.edit_gm_name]

        else:
            gm = vcs.creategraphicsmethod(str(self.gm_type_combo.currentText()),
                                         str(self.gm_instance_combo.currentText()),
                                         str(self.textValue()))
            get_gms().add_gm(gm)

        if self.edit_dialog:
            self.edit_dialog.deleteLater()
            self.edit_dialog = None

    def editGM(self):
        if not self.edit_dialog:
            self.edit_dialog = EditGmDialog(self.gm_type_combo.currentText(), self.gm_instance_combo.currentText())

        self.edit_dialog.show()
        self.edit_dialog.raise_()


class GraphicsMethodWidget(StaticDockWidget):
    editedGM = QtCore.Signal()

    def __init__(self, parent=None, flags=0):
        super(GraphicsMethodWidget, self).__init__("Graphics Methods", parent=parent, flags=flags)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]
        self.setTitleBarWidget(AddEditRemoveToolbar("Graphics Methods",
                                                    self,
                                                    self.add_gm,
                                                    self.edit_gm,
                                                    self.remove_gm))

        self.titleBarWidget().edit.setEnabled(False)
        self.titleBarWidget().remove.setEnabled(False)
        self.list = GraphicsMethodList()
        self.list.changedSelection.connect(self.selection_change)
        self.setWidget(self.list)
        self.add_gm_widget = None
        self.edit_dialog = None
        self.ginstance = None
        self.gtype = None

    def selection_change(self):
        selected = self.list.get_selected()
        self.ginstance = None
        if selected is None:
            return
        if selected:
            self.gtype = selected[0]
            if len(selected) > 1 and self.gtype not in gms_with_non_implemented_editors:
                self.ginstance = selected[1]
                self.titleBarWidget().edit.setEnabled(True)
                self.titleBarWidget().remove.setEnabled(True)
        else:
            self.titleBarWidget().edit.setEnabled(False)
            self.titleBarWidget().remove.setEnabled(False)
            return
        if self.ginstance == 'default':
            self.titleBarWidget().edit.setEnabled(False)
            self.titleBarWidget().remove.setEnabled(False)
            return
        elif not self.ginstance:
            self.titleBarWidget().edit.setEnabled(False)
            self.titleBarWidget().remove.setEnabled(False)
            return

    def add_gm(self):
        self.add_gm_widget = CreateGM(self.list.get_selected())
        self.add_gm_widget.show()
        self.add_gm_widget.raise_()

    def edit_gm(self):
        self.edit_dialog = EditGmDialog(self.gtype, self.ginstance, False)
        self.edit_dialog.accepted.connect(self.editedGM.emit)
        self.edit_dialog.show()
        self.edit_dialog.raise_()

    def remove_gm(self):
        model_index = get_gms().indexOf(self.gtype, vcs.getgraphicsmethod(self.gtype, self.ginstance))
        get_gms().removeRows(model_index.row(), 1, parent=model_index.parent())
