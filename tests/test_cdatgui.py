import pytest  # noqa
import cdatgui
from PySide import QtGui


def test_add_edit_remove_tbar(qtbot):

    called = []

    def add():
        called.append("add")

    def edit():
        called.append("edit")

    def remove():
        called.append("remove")

    bar = cdatgui.toolbars.AddEditRemoveToolbar(u"Title",
                                                add_action=add,
                                                edit_action=edit,
                                                remove_action=remove
                                                )
    qtbot.addWidget(bar)

    bar.add.activate(QtGui.QAction.Trigger)
    bar.edit.activate(QtGui.QAction.Trigger)
    bar.remove.activate(QtGui.QAction.Trigger)

    assert "add" in called
    assert "edit" in called
    assert "remove" in called

    assert bar.windowTitle() == u"Title"
