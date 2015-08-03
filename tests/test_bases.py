import pytest
from PySide import QtGui
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


def test_file_browser(qtbot):
    # Simple directory with a subdir and some files
    fpath = os.path.join(os.path.basename(__file__), "testdir")

    widget = cdatgui.bases.FileBrowserWidget(fpath)
    qtbot.addWidget(widget)

    # Make sure it doesn't default to selecting anything
    assert len(widget.get_selected_files()) == 0
