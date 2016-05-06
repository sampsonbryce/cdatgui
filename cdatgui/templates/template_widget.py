from PySide import QtCore
from cdatgui.bases import StaticDockWidget
from cdatgui.templates import get_templates
from cdatgui.toolbars import AddEditRemoveToolbar
from template_list import TemplateList
from cdatgui.templates.dialog import TemplateEditorDialog
import vcs


class TemplateWidget(StaticDockWidget):
    editedTmpl = QtCore.Signal()

    def __init__(self, parent=None):
        super(TemplateWidget, self).__init__("Templates", parent=parent)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]
        self.setTitleBarWidget(AddEditRemoveToolbar("Templates",
                                                    self,
                                                    self.add_template,
                                                    self.edit_template,
                                                    self.remove_template))
        self.list = TemplateList()
        self.list.changedSelection.connect(self.selection_change)
        self.dialog = None
        self.setWidget(self.list)
        self.titleBarWidget().edit.setEnabled(False)
        self.titleBarWidget().remove.setEnabled(False)

    def selection_change(self):
        selected = self.list.get_selected()
        if selected is None or selected.name == 'default':
            self.titleBarWidget().edit.setEnabled(False)
            self.titleBarWidget().remove.setEnabled(False)
        else:
            self.titleBarWidget().edit.setEnabled(True)
            self.titleBarWidget().remove.setEnabled(True)

    def add_template(self):
        # get template object
        sel = self.list.get_selected()
        if sel is None:
            sel = vcs.gettemplate('default')

        self.dialog = TemplateEditorDialog(sel)
        self.dialog.doneEditing.connect(self.template_edited)

        # remove save button
        v_layout = self.dialog.layout()
        v_layout.itemAt(v_layout.count() - 1).takeAt(3).widget().deleteLater()

        self.dialog.show()
        self.dialog.raise_()

    def edit_template(self):
        sel = self.list.get_selected()
        self.dialog = TemplateEditorDialog(sel)

        #remove save as button
        v_layout = self.dialog.layout()
        v_layout.itemAt(v_layout.count() - 1).takeAt(2).widget().deleteLater()

        self.dialog.doneEditing.connect(self.template_edited)
        self.dialog.show()
        self.dialog.raise_()

    def remove_template(self):
        sel = self.list.get_selected()
        self.list.remove(sel)

    def template_edited(self, *args, **kargs):
        self.editedTmpl.emit()


