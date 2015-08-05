from PySide import QtCore
from cdatgui.bases import StaticDockWidget
from cdatgui.toolbars import AddEditRemoveToolbar
from template_list import TemplateList


class TemplateWidget(StaticDockWidget):
    selectedTemplate = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(TemplateWidget, self).__init__("Templates", parent=parent)
        self.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea]
        self.setTitleBarWidget(AddEditRemoveToolbar("Templates",
                                                    self,
                                                    self.add_template,
                                                    self.edit_template,
                                                    self.remove_template))
        self.list = TemplateList()
        self.list.itemSelectionChanged.connect(self.selection_change)
        self.setWidget(self.list)

    def selection_change(self):
        selected = self.list.get_selected()
        if selected is None:
            return
        self.selectedTemplate.emit(selected)

    def add_template(self):
        pass

    def edit_template(self):
        pass

    def remove_template(self):
        pass
