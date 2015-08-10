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


def test_utils_data_file():
    path = cdatgui.utils.data_file("utils.py")

    module_path = cdatgui.utils.__file__
    if module_path[-3:] == "pyc":
        module_path = module_path[:-1]

    assert path == module_path

    with pytest.raises(IOError):
        cdatgui.utils.data_file("notarealfile.noreally")


def test_utils_icon():
    icon = cdatgui.utils.icon("esgf.png")
    assert type(icon) == QtGui.QIcon
    with pytest.raises(IOError):
        cdatgui.utils.icon("nosuchfile.txt")


def test_utils_flags():
    flagged_val = 3
    assert cdatgui.utils.has_flag(flagged_val, 1)
    assert cdatgui.utils.has_flag(flagged_val, 2)

    assert cdatgui.utils.accum_flags([1, 2, 8]) == 11


def test_utils_labels():
    l = cdatgui.utils.label("Hi There")
    assert type(l) == QtGui.QLabel
    l2 = cdatgui.utils.header_label("Oh Hi")
    assert type(l2) == QtGui.QLabel


def test_main_window(qtbot, clt):
    mw = cdatgui.MainWindow()
    qtbot.addWidget(mw)
    mw.update_var_on_main(clt)
    m = mw.manager

    # Make sure it plotted something
    assert m.dp is not None
