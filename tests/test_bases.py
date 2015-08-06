import pytest  # noqa
from PySide import QtGui, QtCore
import cdatgui
import os


def test_vertical_tabs(qtbot):
    widget = cdatgui.bases.VerticalTabWidget()
    qtbot.addWidget(widget)

    test_widget = QtGui.QTextEdit()
    test_title_1 = u"Title 1"

    test_layout = QtGui.QVBoxLayout()
    test_title_2 = u"Title 2"

    widget.add_widget(test_title_1, test_widget)
    item = widget.item(0)

    # Make sure it properly added the widget
    assert item[0] == test_title_1
    assert item[1] == test_widget

    widget.add_layout(test_title_2, test_layout)

    item = widget.item(1)

    # Make sure it properly added the layout
    assert item[0] == test_title_2
    assert item[1] == test_layout

    # Make sure it defaults to the 0th item
    assert widget.current_row() == 0
    assert widget.current_item() == (test_title_1, test_widget)

    widget.set_current_row(1)

    # Make sure set_current_row updates things correctly
    assert widget.current_row() == 1
    assert widget.current_item() == (test_title_2, test_layout)


def test_directory_list(qtbot):
    fpath = os.path.join(os.path.dirname(__file__), "testdir")
    print fpath
    widget = cdatgui.bases.DirectoryListWidget(QtCore.QDir(fpath),
                                               filetypes=["test"])
    qtbot.addWidget(widget)

    # Make sure it properly sets the name of the directory
    assert widget.name() == "testdir"

    # Make sure it only has the items in the directory (no . or ..)
    assert len(widget.entries) == 3
    assert widget.entries[0].fileName() == "filter_test.test"
    assert widget.entries[0].isFile()
    assert widget.entries[1].fileName() == "subfile.txt"
    assert widget.entries[1].isFile()
    assert widget.entries[2].fileName() == "subfolder"
    assert widget.entries[2].isDir()

    # Make sure filetypes works correctly
    assert widget.list.item(0).flags() != 0  # should be enabled
    assert widget.list.item(1).flags() == 0  # should be disabled

    # Make sure has_item works
    assert widget.has_item(widget.list.item(0))

    with qtbot.waitSignal(widget.list.currentItemChanged,
                          timeout=1000,
                          raising=True):
        widget.list.setCurrentRow(0)


def test_file_browser(qtbot):
    # Simple directory with a subdir and some files
    fpath = os.path.join(os.path.dirname(__file__), "testdir")

    widget = cdatgui.bases.FileBrowserWidget(fpath)
    qtbot.addWidget(widget)

    # Make sure it doesn't default to selecting anything
    assert len(widget.get_selected_files()) == 0

    # Make sure the correct root directory is open
    assert widget.dirs[0].name() == "testdir"
