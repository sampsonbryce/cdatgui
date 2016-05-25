import pytest  # noqa
from PySide import QtGui, QtCore
import cdatgui
import os


def get_fb():
    # Simple directory with a subdir and some files
    fpath = os.path.join(os.path.dirname(__file__), "testdir")

    widget = cdatgui.bases.FileBrowserWidget(fpath)
    return widget


def test_vertical_tabs(qtbot):
    widget = cdatgui.bases.VerticalTabWidget()
    qtbot.addWidget(widget)

    test_widget = QtGui.QTextEdit()
    test_title_1 = u"Title 1"

    test_layout = QtGui.QVBoxLayout()
    test_title_2 = u"Title 2"

    widget.add_widget(test_title_1, test_widget)
    item = widget.item(0)

    # it properly added the widget
    assert item[0] == test_title_1
    assert item[1] == test_widget

    widget.add_layout(test_title_2, test_layout)

    item = widget.item(1)

    # it properly added the layout
    assert item[0] == test_title_2
    assert item[1] == test_layout

    # it defaults to the 0th item
    assert widget.current_row() == 0
    assert widget.current_item() == (test_title_1, test_widget)

    widget.set_current_row(1)

    # set_current_row updates things correctly
    assert widget.current_row() == 1
    assert widget.current_item() == (test_title_2, test_layout)


def test_directory_list(qtbot):
    fpath = os.path.join(os.path.dirname(__file__), "testdir")

    widget = cdatgui.bases.DirectoryListWidget(QtCore.QDir(fpath),
                                               filetypes=["test"])
    qtbot.addWidget(widget)

    # it properly sets the name of the directory
    assert widget.name() == "testdir"

    # it only has the items in the directory (no . or ..)
    assert len(widget.entries) == 3
    assert widget.entries[0].fileName() == "filter_test.test"
    assert widget.entries[0].isFile()
    assert widget.entries[1].fileName() == "subfile.txt"
    assert widget.entries[1].isFile()
    assert widget.entries[2].fileName() == "subfolder"
    assert widget.entries[2].isDir()

    # filetypes works correctly
    assert widget.list.item(0).flags() != 0  # should be enabled
    assert widget.list.item(1).flags() == 0  # should be disabled

    # has_item works
    assert widget.has_item(widget.list.item(0))

    with qtbot.waitSignal(widget.currentItemChanged,
                          timeout=1000,
                          raising=True):
        widget.list.setCurrentRow(0)


def test_file_browser_init(qtbot):
    widget = get_fb()
    qtbot.addWidget(widget)

    # it doesn't default to selecting anything
    assert len(widget.get_selected_files()) == 0

    # it has a directory widget
    assert len(widget.dirs) == 1

    # the correct root directory is open
    assert widget.dirs[0].name() == "testdir"


def test_file_browser_open_directory(qtbot):
    widget = get_fb()
    qtbot.addWidget(widget)

    # selecting a directory opens it as a child
    widget.dirs[0].list.setCurrentRow(2)
    # the new directory is opened
    assert len(widget.dirs) == 2

    # Still report 0 files selected (since only a dir was selected)
    assert len(widget.get_selected_files()) == 0

    # it opened the correct child
    assert widget.dirs[1].name() == "subfolder"

    # Open another child to make sure the scroll works
    widget.dirs[1].list.setCurrentRow(1)

    # it opened the correct child
    assert widget.dirs[2].name() == "subsub"

    # it scrolled all the way to the right
    assert widget.horizontalScrollBar().value() == widget.horizontalScrollBar().maximum()


def test_file_browser_selection(qtbot):
    widget = get_fb()
    qtbot.addWidget(widget)

    # Select a file
    with qtbot.waitSignal(widget.selectionChange, timeout=1000, raising=True):
        widget.dirs[0].list.setCurrentRow(1)

    # it detected the selection
    assert len(widget.get_selected_files()) == 1

    # Select a folder
    with qtbot.waitSignal(widget.selectionChange, timeout=1000, raising=True):
        widget.dirs[0].list.setCurrentRow(2)

    assert len(widget.get_selected_files()) == 0

    with qtbot.waitSignal(widget.selectionChange, timeout=1000, raising=True):
        # Select a file in subfolder
        widget.dirs[1].list.setCurrentRow(0)

    assert len(widget.get_selected_files()) == 1

    with qtbot.waitSignal(widget.selectionChange, timeout=1000, raising=True):
        widget.dirs[0].list.setCurrentRow(1)

    # the child was removed
    assert len(widget.dirs) == 1

    # the new selection was detected
    assert len(widget.get_selected_files()) == 1

    # deselecting properly removes children
    widget.dirs[0].list.setCurrentRow(2)
    widget.dirs[0].list.setCurrentItem(None)

    assert len(widget.dirs) == 1

    widget.dirs[0].list.setCurrentItem(None)
    assert len(widget.dirs) == 1


def test_file_browser_update_root(qtbot):
    widget = get_fb()
    qtbot.addWidget(widget)
    fpath = widget.root.absolutePath()
    # there are two items before changing the root
    widget.dirs[0].list.setCurrentRow(2)

    # Try changing the root
    widget.set_root(os.path.join(fpath, "subfolder"))

    # all children were removed and only one item is there
    assert len(widget.dirs) == 1
    # it's the right item
    assert widget.dirs[0].name() == "subfolder"


def test_static_dock_widget_sides(qtbot):
    w = cdatgui.bases.static_docked.StaticDockWidget("Docked")
    qtbot.addWidget(w)

    w.allowed_sides = [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, QtCore.Qt.DockWidgetArea.RightDockWidgetArea]
    assert w.allowedAreas() == QtCore.Qt.DockWidgetArea.LeftDockWidgetArea | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
    assert len(w.allowed_sides) == 2
    for side in [QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, QtCore.Qt.DockWidgetArea.RightDockWidgetArea]:
        assert side in w.allowed_sides


def test_range_widget(qtbot):
    w = cdatgui.bases.RangeWidget([str(i) for i in range(50)], 10, 40)
    qtbot.addWidget(w)

    assert w.getBounds() == (10, 40)
    w.lowerBoundSlider.setValue(40)
    # w.updateLower(41)
    assert w.getBounds() == (40, 40)
    w.lowerBoundText.setText("12")
    w.lowerBoundText.textEdited.emit("12")
    assert w.getBounds() == (12, 40)
    w.upperBoundSlider.setValue(12)
    # w.updateUpper(12)
    assert w.getBounds() == (12, 12)
    w.upperBoundText.setText("30")
    w.upperBoundText.textEdited.emit("30")
    assert w.getBounds() == (12, 30)

