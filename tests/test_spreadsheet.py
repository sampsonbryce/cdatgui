import pytest
import cdatgui
import vcs
import cdms2
from cdatgui.spreadsheet.window import SpreadsheetWindow

def test_spreadsheet_window(qtbot):
    window = SpreadsheetWindow()
    qtbot.addWidget(window)

    window.fitActionToggled(True)
    window.fitActionToggled(False)

    # Check that it has a canvas
    assert window.getCanvas() is not None

    window.getSelectedLocations()

def test_spreadsheet_tabcontroller(qtbot):
    window = SpreadsheetWindow()
    qtbot.addWidget(window)

    tc = window.tabController

    tc.clearTabs()
    tc.newSheetActionTriggered()
    tc.moveTab(0,0)
    tc.splitTab(0)
    tc.mergeTab(tc.floatingTabWidgets[0],0)
    tc.tabWidgetUnderMouse()
    tc.showNextTab()
    tc.changeSpreadsheetFileName('TestName - (1)')

def test_spreadsheet_tab(qtbot):
    window = SpreadsheetWindow()
    qtbot.addWidget(window)

    tab = window.tabController.currentWidget()

    tab.removeContainers()
    tab.createContainers()
    # Check that it still has a canvas
    assert window.getCanvas() is not None

    tab.toolBar.colCountSpinBox().setValue(3)
    tab.colSpinBoxChanged()
    tab.toolBar.rowCountSpinBox().setValue(3)
    tab.rowSpinBoxChanged()
    assert tab.getDimension() == (3, 3)

    cell = tab.getCellWidget(2, 2)
    assert cell.widget() is not None
    tab.getCellRect(1, 2)
    tab.getCellGlobalRect(2, 1)
    tab.showHelpers(True, None)
    tab.clearSelection()
    assert not tab.getSelectedLocations()
    tab.setSpan(0, 0, 2, 1)
    assert tab.sheet.getRealLocation(1,0) == (0,0)

def test_spreadsheet_sheet(qtbot):
    window = SpreadsheetWindow()
    qtbot.addWidget(window)

    sheet = window.tabController.currentWidget().sheet

    sheet.forceColumnMultiSelect(0)
    sheet.forceColumnMultiSelect(0)
    sheet.forceRowMultiSelect(0)
    sheet.forceRowMultiSelect(0)
    sheet.forceSheetSelect()
    sheet.forceSheetSelect()
    sheet.setFitToWindow(True)
    sheet.resizeEvent(None)
    sheet.setFitToWindow(False)
    sheet.stretchCells()
