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
    def __init__(self, gtype, ginstance):
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

        self.rejected.connect(self.resetGM)

    def resetGM(self):
        if self.edit_gm_name:
            del vcs.elements[self.gtype][self.edit_gm_name]
        self.edit_gm_name = None

    def resetTmpl(self):
        if self.edit_tmpl_name:
            del vcs.elements['template'][self.edit_tmpl_name]
        self.edit_tmpl_name = None


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
        button_layout = self.vertical_layout.itemAt(self.vertical_layout.count() - 1).layout()
        customize_button = QtGui.QPushButton('Customize')
        customize_button.clicked.connect(self.editGM)
        button_layout.insertWidget(1, customize_button)

        self.accepted.connect(self.createGM)

    def setGMRoot(self, index):
        self.edit.validator().gm_type = self.gm_type_combo.currentText()
        self.gm_instance_combo.setRootModelIndex(get_gms().index(index, 0))
        self.gm_instance_combo.setCurrentIndex(self.gm_instance_combo.findText('default'))
        self.edit.validator().validate(self.edit.text(), 0)

    def createGM(self):
        if self.edit_dialog and self.edit_dialog.edit_gm_name:
            get_gms().add_gm(
                vcs.creategraphicsmethod(str(self.gm_type_combo.currentText()),
                                         self.edit_dialog.edit_gm_name,
                                         str(self.textValue())
                                         ))
            del vcs.elements[self.gm_type_combo.currentText()][self.edit_gm_name]

        else:
            get_gms().add_gm(
                vcs.creategraphicsmethod(str(self.gm_type_combo.currentText()),
                                         str(self.gm_instance_combo.currentText()),
                                         str(self.textValue())
                                         ))

    def editGM(self):
        self.edit_dialog = EditGmDialog(self.gm_type_combo.currentText(), self.gm_instance_combo.currentText())

        self.edit_dialog.show()
        self.edit_dialog.raise_()

    def save(self):
        if self.edit_dialog:
            self.edit_dialog.resetTmpl()
        super(CreateGM, self).save()

    def cancel(self):
        if self.edit_dialog:
            self.edit_dialog.resetTmpl()
            self.edit_dialog.resetGM()
        super(CreateGM, self).cancel()


class GraphicsMethodWidget(StaticDockWidget):
    def __init__(self, parent=None, flags=0):
        super(GraphicsMethodWidget, self).__init__("Graphics Methods", parent=parent, flags=flags)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]
        self.setTitleBarWidget(AddEditRemoveToolbar("Graphics Methods",
                                                    self,
                                                    self.add_gm,
                                                    self.edit_gm,
                                                    self.remove_gm))

        self.titleBarWidget().edit.setEnabled(False)
        self.list = GraphicsMethodList()
        self.list.changedSelection.connect(self.selection_change)
        self.setWidget(self.list)
        self.add_gm_widget = None
        self.edit_dialog = None
        self.ginstance = None
        self.gtype = None

    def selection_change(self):
        selected = self.list.get_selected()
        if selected is None:
            return
        if selected:
            self.gtype = selected[0]
            if len(selected) > 1:
                self.ginstance = selected[1]
                self.titleBarWidget().edit.setEnabled(True)
        else:
            self.titleBarWidget().edit.setEnabled(False)
            return
        if self.ginstance == 'default':
            self.titleBarWidget().edit.setEnabled(False)
            return
        elif not self.ginstance:
            self.titleBarWidget().edit.setEnabled(False)
            return

        # self.selectedGraphicsMethod.emit(selected)

    def add_gm(self):
        self.add_gm_widget = CreateGM(self.list.get_selected())
        self.add_gm_widget.show()
        self.add_gm_widget.raise_()

    def edit_gm(self):
        self.edit_dialog = EditGmDialog(self.gtype, self.ginstance)

        self.edit_dialog.show()
        self.edit_dialog.raise_()

    def remove_gm(self):
        pass
