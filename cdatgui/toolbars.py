from PySide import QtGui, QtCore
from utils import icon, Spacer, header_label


add_icon = None
edit_icon = None
remove_icon = None


def init_icons():
    global add_icon, edit_icon, remove_icon
    if add_icon is None or edit_icon is None or remove_icon is None:
        add_icon = icon("edit_add.png")
        edit_icon = icon("edit.png")
        remove_icon = icon("editdelete.png")


class AddEditRemoveToolbar(QtGui.QToolBar):

    def __init__(self, title, parent=None, add_action=None, edit_action=None,
                 remove_action=None):

        super(AddEditRemoveToolbar, self).__init__(title, parent=parent)

        # Sane defaults
        self.setIconSize(QtCore.QSize(16, 16))
        self.setMovable(False)

        init_icons()

        self.addWidget(Spacer(width=5, parent=self))

        # Add the title as a label
        self.addWidget(header_label(title))

        self.addWidget(Spacer(parent=self))

        if add_action is not None:
            self.addAction(add_icon, u"Add", add_action)

        if edit_action is not None:
            self.addAction(edit_icon, u"Edit", edit_action)

        if remove_action is not None:
            self.addAction(remove_icon, u"Remove", remove_action)
