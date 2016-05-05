###############################################################################
##
## Copyright (C) 2014-2015, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

"""This file implements the Spreadsheet Tab Controller, to manages tabs:
StandardWidgetTabController
"""

from __future__ import division

from ast import literal_eval
import copy
import gc
import os.path
from PySide import QtCore, QtGui

from .tab import StandardWidgetTabBar, StandardWidgetSheetTab, \
    StandardTabDockWidget


class StandardWidgetTabController(QtGui.QTabWidget):
    """
    StandardWidgetTabController inherits from QTabWidget to contain a
    list of StandardWidgetSheetTab. This is the major component that
    will handle most of the spreadsheet actions

    """
    needChangeTitle = QtCore.Signal()
    tabCloseRequested = QtCore.Signal()
    selectionChanged = QtCore.Signal(list)
    emitAllPlots = QtCore.Signal(list)

    def __init__(self, parent=None):
        """ StandardWidgetTabController(parent: QWidget)
                                        -> StandardWidgetTabController
        Initialize signals/slots and widgets for the tab bar

        """

        QtGui.QTabWidget.__init__(self, parent)
        self.operatingWidget = self
        self.setTabBar(StandardWidgetTabBar(self))
        self.setTabShape(QtGui.QTabWidget.Triangular)
        self.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidgets = []
        self.floatingTabWidgets = []
        self.create_first_sheet()
        self.tabBar().tabMoveRequest.connect(self.moveTab)
        self.tabBar().tabSplitRequest.connect(self.splitTab)
        self.tabBar().tabTextChanged.connect(self.changeTabText)
        self.addAction(self.showNextTabAction())
        self.addAction(self.showPrevTabAction())
        self.executedPipelines = [[], {}, {}]
        self.monitoredPipelines = {}
        self.spreadsheetFileName = None
        self.tabCloseRequested.connect(self.delete_sheet_by_index)

    def create_first_sheet(self):
        self.addTabWidget(StandardWidgetSheetTab(self), 'Sheet 1')

    def newSheetAction(self):
        """ newSheetAction() -> QAction
        Return the 'New Sheet' action

        """
        if not hasattr(self, 'newSheetActionVar'):
            icon = QtGui.QIcon(':/images/newsheet.png')
            self.newSheetActionVar = QtGui.QAction(icon, '&New sheet', self)
            self.newSheetActionVar.setToolTip('Create a new sheet')
            self.newSheetActionVar.setStatusTip('Create and show a new sheet')
            self.newSheetActionVar.setShortcut(QtGui.QKeySequence('Ctrl+N'))
            self.newSheetActionVar.triggered.connect(self.newSheetActionTriggered)
        return self.newSheetActionVar

    def deleteSheetAction(self):
        """ deleteSheetAction() -> QAction
        Return the 'Delete Sheet' action:

        """
        if not hasattr(self, 'deleteSheetActionVar'):
            icon = QtGui.QIcon(':/images/deletesheet.png')
            self.deleteSheetActionVar = QtGui.QAction(icon, '&Delete sheet',
                                                      self)
            self.deleteSheetActionVar.setToolTip('Delete the current sheet')
            self.deleteSheetActionVar.setStatusTip('Delete the current sheet '
                                                   'if there are more than one')
            key = QtGui.QKeySequence('Ctrl+Backspace')
            self.deleteSheetActionVar.setShortcut(key)
            self.connect(self.deleteSheetActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.deleteSheetActionTriggered)
        return self.deleteSheetActionVar

    def showNextTabAction(self):
        """ showNextTabAction() -> QAction
        Return the 'Next Sheet' action

        """
        if not hasattr(self, 'showNextTabActionVar'):
            icon = QtGui.QIcon(':/images/forward.png')
            self.showNextTabActionVar = QtGui.QAction(icon, '&Next sheet', self)
            self.showNextTabActionVar.setToolTip('Show the next sheet')
            self.showNextTabActionVar.setStatusTip('Show the next sheet if it '
                                                   'is available')
            self.showNextTabActionShortcut = QtGui.QShortcut(self)
            self.showNextTabActionVar.setShortcut('Ctrl+PgDown')
            self.connect(self.showNextTabActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.showNextTab)
        return self.showNextTabActionVar

    def showPrevTabAction(self):
        """ showPrevTabAction() -> QAction
        Return the 'Prev Sheet' action

        """
        if not hasattr(self, 'showPrevTabActionVar'):
            icon = QtGui.QIcon(':/images/back.png')
            self.showPrevTabActionVar = QtGui.QAction(icon, '&Prev sheet', self)
            self.showPrevTabActionVar.setToolTip('Show the previous sheet')
            self.showPrevTabActionVar.setStatusTip('Show the previous sheet if '
                                                   'it is available')
            self.showPrevTabActionVar.setShortcut('Ctrl+PgUp')
            self.connect(self.showPrevTabActionVar,
                         QtCore.SIGNAL('triggered()'),
                         self.showPrevTab)
        return self.showPrevTabActionVar

    def uvcdatPreferencesAction(self):
        """ uvcdatAutoExecuteAction(self) -> QAction
        It will show a popup with preferences

        """
        if not hasattr(self, 'uvcdatPreferencesVar'):
            self.uvcdatPreferencesVar = QtGui.QAction(UVCDATTheme.PREFERENCES_ICON,
                                                      'Sheet Options',
                                                      self)
            self.uvcdatPreferencesVar.setStatusTip("Show Sheet Options")

            prefMenu = QtGui.QMenu(self)
            executeAction = prefMenu.addAction("Auto-Execute")
            executeAction.setStatusTip(
                'Execute visualization automatically after changes')
            executeAction.setCheckable(True)
            conf = get_vistrails_configuration()
            checked = True
            if conf.has('uvcdat'):
                checked = conf.uvcdat.check('autoExecute')
            executeAction.setChecked(checked)

            aspectAction = prefMenu.addAction("Keep Aspect Ratio in VCS plots")
            aspectAction.setStatusTip("Keep Aspect Ratio in VCS plots")
            aspectAction.setCheckable(True)
            checked = True
            if conf.has('uvcdat'):
                checked = conf.uvcdat.check('aspectRatio')
            aspectAction.setChecked(checked)

            exportMenu = prefMenu.addMenu("Export Sheet")
            singleAction = exportMenu.addAction('As a Single Image...')
            multiAction = exportMenu.addAction('Separately...')
            self.connect(singleAction,
                         QtCore.SIGNAL('triggered()'),
                         self.exportSheetToSingleImageActionTriggered)
            self.connect(multiAction,
                         QtCore.SIGNAL('triggered()'),
                         self.exportSheetToSeparateImagesActionTriggered)

            themeMenu = prefMenu.addMenu("Icons Theme")
            defaultThemeAction = themeMenu.addAction("Default")
            defaultThemeAction.setCheckable(True)
            defaultThemeAction.setStatusTip(
                "Use the default theme (the application must be restarted for changes to take effect)")

            minimalThemeAction = themeMenu.addAction("Minimal")
            minimalThemeAction.setCheckable(True)
            minimalThemeAction.setStatusTip(
                "Use the minimal theme (the application must be restarted for changes to take effect)")
            themegroup = QtGui.QActionGroup(self)
            themegroup.addAction(defaultThemeAction)
            themegroup.addAction(minimalThemeAction)
            if conf.uvcdat.theme == "Default":
                defaultThemeAction.setChecked(True)
            elif conf.uvcdat.theme == "Minimal":
                minimalThemeAction.setChecked(True)

            self.uvcdatPreferencesVar.setMenu(prefMenu)

            self.connect(executeAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.uvcdatAutoExecuteActionTriggered)
            self.connect(aspectAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.uvcdatAspectRatioActionTriggered)
            self.connect(defaultThemeAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.uvcdatDefaultThemeActionTriggered)
            self.connect(minimalThemeAction,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.uvcdatMinimalThemeActionTriggered)
        return self.uvcdatPreferencesVar

    def exportSheetToImageAction(self):
        """ exportSheetToImageAction() -> QAction
        Export the current sheet to an image

        """
        if not hasattr(self, 'exportSheetToImageVar'):
            self.exportSheetToImageVar = QtGui.QAction('Export Sheet', self)
            self.exportSheetToImageVar.setStatusTip(
                'Export all cells in the spreadsheet to a montaged image')

            exportMenu = QtGui.QMenu(self)
            singleAction = exportMenu.addAction('As a Single Image')
            multiAction = exportMenu.addAction('Separately')
            self.exportSheetToImageVar.setMenu(exportMenu)

            self.connect(self.exportSheetToImageVar,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.exportSheetToSingleImageActionTriggered)

            self.connect(singleAction,
                         QtCore.SIGNAL('triggered()'),
                         self.exportSheetToSingleImageActionTriggered)
            self.connect(multiAction,
                         QtCore.SIGNAL('triggered()'),
                         self.exportSheetToSeparateImagesActionTriggered)
        return self.exportSheetToImageVar

    def exportSheetToSingleImageActionTriggered(self, action=None):
        """ exportSheetToSingleImageActionTriggered() -> None
        Exports the sheet as a big image
        """
        filename = QtGui.QFileDialog.getSaveFileName(
            self, "Select a File to Export the Sheet",
            ".", "Images (*.png *.xpm *.jpg)")
        if filename:
            self.currentWidget().exportSheetToImage(filename)

    def exportSheetToSeparateImagesActionTriggered(self, action=None):
        """ exportSheetToSeparateImagesActionTriggered() -> None
        Exports the cells as separate images
        """
        dirname = QtGui.QFileDialog.getExistingDirectory(
            self, 'Select a Directory to Export Images', ".",
            QtGui.QFileDialog.ShowDirsOnly)
        if dirname:
            self.currentWidget().exportSheetToImages(dirname)

    def newSheetActionTriggered(self, checked=False):
        """ newSheetActionTriggered(checked: boolean) -> None
        Actual code to create a new sheet

        """
        self.setCurrentIndex(self.addTabWidget(StandardWidgetSheetTab(self),
                                               'Sheet %d' % (self.count() + 1)))
        self.currentWidget().sheet.stretchCells()

    def tabInserted(self, index):
        """tabInserted(index: int) -> None
        event handler to get when sheets are inserted """
        self.deleteSheetAction().setEnabled(True)

    def tabRemoved(self, index):
        """tabInserted(index: int) -> None
        event handler to get when sheets are removed """
        if self.count() == 0:
            self.deleteSheetAction().setEnabled(False)

    def delete_sheet_by_index(self, index):
        widget = self.widget(index)
        widget.deleteAllCells()
        self.emit(QtCore.SIGNAL("remove_tab"), widget)
        self.tabWidgets.remove(widget)
        self.removeTab(index)
        self.removeSheetReference(widget)
        widget.deleteLater()
        QtCore.QCoreApplication.processEvents()
        gc.collect()

    def deleteSheetActionTriggered(self, checked=False):
        """ deleteSheetActionTriggered(checked: boolean) -> None
        Actual code to delete the current sheet

        """
        if self.count() > 0:
            widget = self.currentWidget()
            self.tabWidgets.remove(widget)
            self.removeTab(self.currentIndex())
            widget.deleteAllCells()
            widget.deleteLater()
            QtCore.QCoreApplication.processEvents()
            gc.collect()

    def clearTabs(self):
        """ clearTabs() -> None
        Clear and reset the controller

        """
        while self.count() > 0:
            self.deleteSheetActionTriggered()
        for i in reversed(range(len(self.tabWidgets))):
            t = self.tabWidgets[i]
            del self.tabWidgets[i]
            self.removeSheetReference(t)
            t.deleteAllCells()
            t.deleteLater()

    def insertTab(self, idx, tabWidget, tabText):
        """ insertTab(idx: int, tabWidget: QWidget, tabText: str)
                      -> QTabWidget
        Redirect insertTab command to operatingWidget, this can either be a
        QTabWidget or a QStackedWidget

        """
        if self.operatingWidget != self:
            ret = self.operatingWidget.insertWidget(idx, tabWidget)
            self.operatingWidget.setCurrentIndex(ret)
            return ret
        else:
            return QtGui.QTabWidget.insertTab(self, idx, tabWidget, tabText)

    def findSheet(self, sheetReference):
        """ findSheet(sheetReference: subclass(SheetReference)) -> Sheet widget
        Find/Create a sheet that meets a certain sheet reference

        """
        if not sheetReference:
            return None
        sheetReference.clearCandidate()
        for idx in xrange(len(self.tabWidgets)):
            tabWidget = self.tabWidgets[idx]
            tabLabel = tabWidget.windowTitle()
            sheetReference.checkCandidate(tabWidget, tabLabel, idx,
                                          self.operatingWidget.currentIndex())
        return sheetReference.setupCandidate(self)

    def changeTabText(self, tabIdx, newTabText):
        """ changeTabText(tabIdx: int, newTabText: str) -> None
        Update window title on the operating widget when the tab text
        has changed

        """
        self.operatingWidget.widget(tabIdx).setWindowTitle(newTabText)

    def moveTab(self, tabIdx, destination):
        """ moveTab(tabIdx: int, destination: int) -> None
        Move a tab at tabIdx to a different position at destination

        """
        if (tabIdx < 0 or tabIdx > self.count() or
                    destination < 0 or destination > self.count()):
            return
        tabText = self.tabText(tabIdx)
        tabWidget = self.widget(tabIdx)
        self.removeTab(tabIdx)
        self.insertTab(destination, tabWidget, tabText)
        if tabIdx == self.currentIndex():
            self.setCurrentIndex(destination)

    def splitTab(self, tabIdx, pos=None):
        """ splitTab(tabIdx: int, pos: QPoint) -> None
        Split a tab to be  a stand alone window and move to position pos

        """
        if tabIdx < 0 or tabIdx > self.count() or self.count() == 0:
            return
        tabWidget = self.widget(tabIdx)
        self.removeTab(tabIdx)

        frame = StandardTabDockWidget(tabWidget.windowTitle(), tabWidget,
                                      self.tabBar(), self)
        if pos:
            frame.move(pos)
        frame.show()
        self.floatingTabWidgets.append(frame)

    def mergeTab(self, frame, tabIdx):
        """ mergeTab(frame: StandardTabDockWidget, tabIdx: int) -> None
        Merge a tab dock widget back to the controller at position tabIdx

        """
        if tabIdx < 0 or tabIdx > self.count():
            return
        if tabIdx == self.count(): tabIdx = -1
        tabWidget = frame.widget()
        frame.setWidget(None)
        while frame in self.floatingTabWidgets:
            self.floatingTabWidgets.remove(frame)
        frame.deleteLater()
        tabWidget.setParent(None)
        newIdx = self.insertTab(tabIdx, tabWidget, tabWidget.windowTitle())
        self.setCurrentIndex(newIdx)

    def addTabWidget(self, tabWidget, sheetLabel):
        """ addTabWidget(tabWidget: QWidget, sheetLabel: str) -> int
        Add a new tab widget to the controller
        """
        tabWidget.selectionChanged.connect(self.selectionChanged.emit)
        tabWidget.emitAllPlots.connect(self.emitAllPlots.emit)
        return self.insertTabWidget(-1, tabWidget, sheetLabel)

    def insertTabWidget(self, index, tabWidget, sheetLabel):
        """ insertTabWidget(index: int, tabWidget: QWidget, sheetLabel: str)
                            -> int
        Insert a tab widget to the controller at some location

        """
        if sheetLabel == None:
            sheetLabel = 'Sheet %d' % (len(self.tabWidgets) + 1)
        if not tabWidget in self.tabWidgets:
            self.tabWidgets.append(tabWidget)
            tabWidget.setWindowTitle(sheetLabel)
        return self.insertTab(index, tabWidget, sheetLabel)

    def tabWidgetUnderMouse(self):
        """ tabWidgetUnderMouse() -> QWidget
        Return the tab widget that is under mouse, hide helpers for the rest

        """
        result = None
        for t in self.tabWidgets:
            if t.underMouse():
                result = t
            else:
                t.showHelpers(False, QtCore.QPoint(-1, -1))
        return result

    def showNextTab(self):
        """ showNextTab() -> None
        Bring the next tab up

        """
        if self.operatingWidget.currentIndex() < self.operatingWidget.count() - 1:
            index = self.operatingWidget.currentIndex() + 1
            self.operatingWidget.setCurrentIndex(index)

    def showPrevTab(self):
        """ showPrevTab() -> None
        Bring the previous tab up

        """
        if self.operatingWidget.currentIndex() > 0:
            index = self.operatingWidget.currentIndex() - 1
            self.operatingWidget.setCurrentIndex(index)

    def tabPopupMenu(self):
        """ tabPopupMenu() -> QMenu
        Return a menu containing a list of all tabs

        """
        menu = QtGui.QMenu(self)
        en = self.operatingWidget.currentIndex() < self.operatingWidget.count() - 1
        self.showNextTabAction().setEnabled(en)
        menu.addAction(self.showNextTabAction())
        en = self.operatingWidget.currentIndex() > 0
        self.showPrevTabAction().setEnabled(en)
        menu.addAction(self.showPrevTabAction())
        menu.addSeparator()
        for idx in xrange(self.operatingWidget.count()):
            t = self.operatingWidget.widget(idx)
            action = menu.addAction(t.windowTitle())
            action.setData(idx)
            if t == self.operatingWidget.currentWidget():
                action.setIcon(QtGui.QIcon(':/images/ok.png'))
        return menu

    def showPopupMenu(self):
        """ showPopupMenu() -> None
        Activate the tab list and show the popup menu

        """
        menu = self.tabPopupMenu()
        action = menu.exec_(QtGui.QCursor.pos())
        self.showNextTabAction().setEnabled(True)
        self.showPrevTabAction().setEnabled(True)
        if not action: return
        if not action in self.actions():
            self.operatingWidget.setCurrentIndex(action.data()[0])
        menu.deleteLater()

    def changeSpreadsheetFileName(self, fileName):
        """ changeSpreadsheetFileName(fileName: str) -> None
        Change the current spreadsheet filename and reflect it on the
        window title

        """
        self.spreadsheetFileName = fileName
        if self.spreadsheetFileName:
            displayName = self.spreadsheetFileName
        else:
            displayName = 'Untitled'
        self.emit(QtCore.SIGNAL('needChangeTitle'),
                  '%s - VisTrails Spreadsheet' % displayName)

    def cleanup(self):
        """ cleanup() -> None
        Clear reference of non-collectable objects/temp files for gc

        """
        self.clearTabs()
