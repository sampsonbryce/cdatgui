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

"""This file implements the main spreadsheet window: SpreadsheetWindow
"""

from __future__ import division

import ctypes
from PySide import QtCore, QtGui
import tempfile

from .base import StandardSheetReference
from .cell import QCellContainer
from .sheet import StandardWidgetSheet
from .tabcontroller import StandardWidgetTabController


class SpreadsheetWindow(QtGui.QMainWindow):
    """
    SpreadsheetWindow is the top-level main window containing a
    stacked widget of QTabWidget

    """
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        """ SpreadsheetWindow(parent: QWidget, f: WindowFlags)
                              -> SpreadsheetWindow
        Layout menu, status bar and tab widget

        """
        QtGui.QMainWindow.__init__(self, parent, f)
        self.shownConfig = False #flag to control the window setup code is done only once
        # The stack of current spreadsheets
        self.stackedCentralWidget = QtGui.QStackedWidget(self)
        # The controller that handles the spreadsheets
        self.tabController = StandardWidgetTabController(self.stackedCentralWidget)
        self.stackedCentralWidget.addWidget(self.tabController)
        self.setCentralWidget(self.stackedCentralWidget)
        self.setStatusBar(QtGui.QStatusBar(self))

        self.App = QtCore.QCoreApplication.instance()
        self.App.installEventFilter(self)

        self.setupMenu()

        self.tabController.needChangeTitle.connect(self.setWindowTitle)

        self.quitAction = QtGui.QAction('&Quit Spreadsheet', self)
        self.addAction(self.quitAction)
        self.quitAction.setShortcut('Ctrl+Q')
        self.quitAction.triggered.connect(self.quitActionTriggered)

    def quitActionTriggered(self):
        self.close()

    def cleanup(self):
        pass

    def destroy(self):
        pass

    def setupMenu(self):
        """ setupMenu() -> None
        Add all available actions to the menu bar

        """
        self.setMenuBar(QtGui.QMenuBar(self))
        self.mainMenu = QtGui.QMenu('&Main', self.menuBar())
        self.menuBar().addAction(self.mainMenu.menuAction())
        #self.mainMenu.addAction(self.tabController.saveAction())
        #self.mainMenu.addAction(self.tabController.saveAsAction())
        #self.mainMenu.addAction(self.tabController.openAction())
        #self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.tabController.newSheetAction())
        self.mainMenu.addAction(self.tabController.deleteSheetAction())
        self.viewMenu = QtGui.QMenu('&View', self.menuBar())
        #self.menuBar().addAction(self.viewMenu.menuAction())
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAction())
        self.windowMenu = QtGui.QMenu('&Window', self.menuBar())
        self.menuBar().addAction(self.windowMenu.menuAction())

    def fitToWindowAction(self):
        """ fitToWindowAction() -> QAction
        Return the fit to window action

        """
        if not hasattr(self, 'fitAction'):
            self.fitAction = QtGui.QAction('Fit to window', self)
            self.fitAction.setStatusTip('Stretch spreadsheet cells '
                                        'to fit the window size')
            self.fitAction.setCheckable(True)
            checked = self.tabController.currentWidget().sheet.fitToWindow
            self.fitAction.setChecked(checked)
            self.connect(self.fitAction,
                         QtCore.SIGNAL('toggled(bool)'),
                         self.fitActionToggled)
        return self.fitAction

    def fitActionToggled(self, checked):
        """ fitActionToggled(checked: boolean) -> None
        Handle fitToWindow Action toggled

        """
        self.tabController.currentWidget().sheet.setFitToWindow(checked)


    def showEvent(self, e):
        """ showEvent(e: QShowEvent) -> None
        Make sure we show ourself for show event

        """
        self.show()
        # Without this Ubuntu Unity will not show the menu bar
        self.raise_()

    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None
        When close, just hide instead

        """
        QtGui.QMainWindow.closeEvent(self, e)

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return a default size of the window

        """
        #return QtCore.QSize(1024, 768)
        return QtCore.QSize(600, 800)

    def eventFilter(self, q, e):
        """ eventFilter(q: QObject, e: QEvent) -> depends on event type
        An application-wide eventfilter to capture mouse/keyboard events

        """
        eType = e.type()
        tabController = self.tabController

        # Handle Show/Hide cell resizer on MouseMove
        if eType==QtCore.QEvent.MouseMove:
            sheetWidget = tabController.tabWidgetUnderMouse()
            if sheetWidget:
                sheetWidget.showHelpers(True, QtGui.QCursor.pos())

        # Perform single-click event on the spreadsheet
        if (eType==QtCore.QEvent.MouseButtonPress):
            if isinstance(q, QCellContainer):
                return q.containedWidget!=None
            p = q
            while (p and (not p.isModal()) and not isinstance(p, StandardWidgetSheet) and p.parent):
                p = p.parent()
            if p and isinstance(p, StandardWidgetSheet) and not p.isModal():
                pos = p.viewport().mapFromGlobal(e.globalPos())
                p.activateCell.emit(p.rowAt(pos.y()), p.columnAt(pos.x()),
                                     e.modifiers()==QtCore.Qt.ControlModifier)
        return False
        #return QtGui.QMainWindow.eventFilter(self,q,e)

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Handle all special events from spreadsheet controller

        """
        return QtGui.QMainWindow.event(self, e)

    def repaintCurrentSheetEvent(self, e):
        """ repaintCurrentSheetEvent(e: RepaintCurrentSheetEvent) -> None
        Repaint the current sheet

        """
        currentTab = self.tabController.currentWidget()
        if currentTab:
            (rCount, cCount) = currentTab.getDimension()
            for r in xrange(rCount):
                for c in xrange(cCount):
                    widget = currentTab.getCell(r, c)
                    if widget:
                        widget.repaint()

    def getCell(self, row=0, col=0):
        reference = StandardSheetReference()
        sheet = self.tabController.findSheet(reference)
        cell = sheet.getCell(row, col)
        return cell

    def getCanvas(self, row=0, col=0):
        # return canvas for specified position in current sheet
        reference = StandardSheetReference()
        sheet = self.tabController.findSheet(reference)
        cell = sheet.getCell(row, col)
        return cell.canvas

    def getSelectedLocations(self):
        # return canvas for specified position in current sheet
        reference = StandardSheetReference()
        sheet = self.tabController.findSheet(reference)
        return sheet.getSelectedLocations()
