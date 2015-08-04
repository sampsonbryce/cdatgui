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
from .tabcontroller_stack import TabControllerStack


class SpreadsheetWindow(QtGui.QMainWindow):
    """
    SpreadsheetWindow is the top-level main window containing a
    stacked widget of QTabWidget and its stacked widget for slideshow
    mode

    """
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        """ SpreadsheetWindow(parent: QWidget, f: WindowFlags)
                              -> SpreadsheetWindow
        Layout menu, status bar and tab widget

        """
        QtGui.QMainWindow.__init__(self, parent, f)
        self.setWindowTitle('UV-CDAT - Untitled')
        self.shownConfig = False #flag to control the window setup code is done only once
        # The stack of current spreadsheets
        self.stackedCentralWidget = QtGui.QStackedWidget(self)
        # The controller that handles the spreadsheets
        self.tabControllerStack = TabControllerStack(self.stackedCentralWidget)
        # FIXME: Temprary create view for now
        self.tabControllerStack.add_view('Default')
        self.stackedCentralWidget.addWidget(self.tabControllerStack)
        # Do we need fullscreen?
        self.fullScreenStackedWidget = QtGui.QStackedWidget(
            self.stackedCentralWidget)
        self.stackedCentralWidget.addWidget(self.fullScreenStackedWidget)
        self.setCentralWidget(self.stackedCentralWidget)
        self.setStatusBar(QtGui.QStatusBar(self))
        self.modeActionGroup = QtGui.QActionGroup(self)

        self.App = QtCore.QCoreApplication.instance()
        self.App.installEventFilter(self)

        self.setupMenu()

        self.tabControllerStack.needChangeTitle.connect(self.setWindowTitle)

        self.quitAction = QtGui.QAction('&Quit Spreadsheet', self)
        self.addAction(self.quitAction)
        self.quitAction.setShortcut('Ctrl+Q')
        self.quitAction.triggered.connect(self.quitActionTriggered)

    def get_current_tab_controller(self):
        return self.tabControllerStack.currentWidget()

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
        self.mainMenu.addAction(self.tabControllerStack.new_tab_action)
        #self.mainMenu.addAction(self.tabController.deleteSheetAction())
        self.viewMenu = QtGui.QMenu('&View', self.menuBar())
        #self.menuBar().addAction(self.viewMenu.menuAction())
        self.viewMenu.addAction(self.interactiveModeAction())
        self.viewMenu.addAction(self.editingModeAction())
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAction())
        self.viewMenu.addAction(self.fullScreenAction())
        self.windowMenu = QtGui.QMenu('&Window', self.menuBar())
        self.menuBar().addAction(self.windowMenu.menuAction())

        self.modeActionGroup.triggered.connect(self.modeChanged)

    def fitToWindowAction(self):
        """ fitToWindowAction() -> QAction
        Return the fit to window action

        """
        if not hasattr(self, 'fitAction'):
            self.fitAction = QtGui.QAction('Fit to window', self)
            self.fitAction.setStatusTip('Stretch spreadsheet cells '
                                        'to fit the window size')
            self.fitAction.setCheckable(True)
            checked = self.tabControllerStack.currentWidget().currentWidget().sheet.fitToWindow
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

    def fullScreenAction(self):
        """ fullScreenAction() -> QAction
        Return the fullscreen action

        """
        if not hasattr(self, 'fullScreenActionVar'):
            self.fullScreenActionVar = QtGui.QAction('&Full Screen', self)
            self.fullScreenActionVar.setShortcut('Ctrl+F')
            self.fullScreenActionVar.setCheckable(True)
            self.fullScreenActionVar.setChecked(False)
            self.fullScreenActionVar.setStatusTip('Show sheets without any '
                                                  'menubar or statusbar')
            self.connect(self.fullScreenActionVar,
                         QtCore.SIGNAL('triggered(bool)'),
                         self.fullScreenActivated)
            self.fullScreenAlternativeShortcuts = [QtGui.QShortcut('F11', self),
                                                   QtGui.QShortcut('Alt+Return',
                                                                   self),
                                                   QtGui.QShortcut('Alt+Enter',
                                                                   self)]
            for sc in self.fullScreenAlternativeShortcuts:
                self.connect(sc, QtCore.SIGNAL('activated()'),
                             self.fullScreenActionVar.trigger)
        return self.fullScreenActionVar

    def fullScreenActivated(self, full=None):
        """ fullScreenActivated(full: bool) -> None
        if fullScreen has been requested has pressed, then go to fullscreen now

        """
        if full==None:
            fs = self.isFullScreen()
            fs = not fs
        else:
            fs = full
        if fs:
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowNoState)
        fs = self.isFullScreen()
        self.menuBar().setVisible(not fs)
        self.statusBar().setVisible(not fs)
        self.tabController.setupFullScreenWidget(fs,
                                                 self.fullScreenStackedWidget)
        self.stackedCentralWidget.setCurrentIndex(int(fs))

    def interactiveModeAction(self):
        """ interactiveModeAction() -> QAction
        Return the interactive mode action, this is the mode where users can
        interact with the content of the cells

        """
        if not hasattr(self, 'interactiveModeActionVar'):
            self.interactiveModeActionVar = QtGui.QAction('&Interactive Mode',
                                                          self.modeActionGroup)
            self.interactiveModeActionVar.setCheckable(True)
            self.interactiveModeActionVar.setChecked(True)
            self.interactiveModeActionVar.setShortcut('Ctrl+Shift+I')
            self.interactiveModeActionVar.setStatusTip('Use this mode to '
                                                       'interact with '
                                                       'the cell contents')
        return self.interactiveModeActionVar

    def editingModeAction(self):
        """ editingModeAction() -> QAction
        Return the editing mode action, this is the mode where users can
        interact with the content of the cells

        """
        if not hasattr(self, 'editingModeActionVar'):
            self.editingModeActionVar = QtGui.QAction('&Editing Mode',
                                                      self.modeActionGroup)
            self.editingModeActionVar.setCheckable(True)
            self.editingModeActionVar.setShortcut('Ctrl+Shift+E')
            self.editingModeActionVar.setStatusTip('Use this mode to '
                                                   'layout cells and '
                                                   'interact cells with '
                                                   'the builder')
        return self.editingModeActionVar

    def modeChanged(self, action):
        """ modeChanged(action: QAction) -> None
        Handle the new mode (interactive or editing) based on the
        triggered action

        """
        editing = self.editingModeAction().isChecked()
        self.tabController.setEditingMode(editing)

    def configShow(self, show=False):
        """ configShow() -> None
        Read VisTrails setting and show the spreadsheet window accordingly

        """
        # TODO show according to config
        return
        if hasattr(self.visApp, 'configuration'):
            if self.shownConfig:
                self.show()
            ### Multiheads
            desktop = QtGui.QApplication.desktop()
            if self.visApp.temp_configuration.multiHeads and desktop.numScreens()>1:
                builderScreen = desktop.screenNumber(self.visApp.builderWindow)
                r = desktop.availableGeometry(builderScreen)
                self.visApp.builderWindow.ensurePolished()
                self.visApp.builderWindow.updateGeometry()
                frame = self.visApp.builderWindow.frameGeometry()
                rect = self.visApp.builderWindow.rect()
                frameDiff = QtCore.QPoint((frame.width()-rect.width())//2,
                                          (frame.height()-rect.height())//2)
                self.visApp.builderWindow.move(
                    frame.topLeft()+r.center()-frame.center())
                for i in xrange(desktop.numScreens()):
                    if i!=builderScreen:
                        r = desktop.availableGeometry(i)
                        self.adjustSize()
                        self.move(r.center()-self.rect().center()-frameDiff)
                        break
            if self.visApp.temp_configuration.batch:
                self.shownConfig = True
                if show:
                    self.show()
                return
            ### Maximize
            if self.visApp.temp_configuration.maximizeWindows:
                self.showMaximized()
                ### When the builder is hidden, the spreadsheet window does
                ### not have focus. We have to force it
                if not self.visApp.temp_configuration.showWindow:
                    self.raise_()
            else:
                self.show()
                ### When the builder is hidden, the spreadsheet window does
                ### not have focus. We have to force it to have the focus
                if not self.visApp.temp_configuration.showWindow:
                    self.raise_()
        else:
            self.show()

        self.shownConfig = True

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

    def eventFilter(self,q,e):
        """ eventFilter(q: QObject, e: QEvent) -> depends on event type
        An application-wide eventfilter to capture mouse/keyboard events

        """
        eType = e.type()
        tabController = self.get_current_tab_controller()

        # Handle Show/Hide cell resizer on MouseMove
        if eType==QtCore.QEvent.MouseMove:
            sheetWidget = tabController.tabWidgetUnderMouse()
            if sheetWidget:
                sheetWidget.showHelpers(True, QtGui.QCursor.pos())

        # Slideshow mode
        if (eType==QtCore.QEvent.MouseButtonPress and
            self.isFullScreen() and
            e.buttons()&QtCore.Qt.RightButton):
            tabController.showPopupMenu()
            return True

        # Handle slideshow shortcuts
        if (eType==QtCore.QEvent.KeyPress and
            self.isFullScreen()):
            if (e.key() in [QtCore.Qt.Key_Space,
                            QtCore.Qt.Key_PageDown,QtCore.Qt.Key_Right]):
                tabController.showNextTab()
                return True
            if (e.key() in [QtCore.Qt.Key_PageUp,QtCore.Qt.Key_Left]):
                tabController.showPrevTab()
                return True
            if (e.key()==QtCore.Qt.Key_Escape or
                (e.key()==QtCore.Qt.Key_F and e.modifiers()&QtCore.Qt.ControlModifier)):
                fullScreenAction().trigger()
                return True

        # Perform single-click event on the spreadsheet
        if (not tabController.editingMode and
            eType==QtCore.QEvent.MouseButtonPress):
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

    def testPlot(self):
        """ displayCellEvent(e: DisplayCellEvent) -> None
        Display a cell when receive this event

        """
        # FIXME: TEST Widget
        #widget = QtGui.QLabel("I am a useless widget!")

        # Add widget to spreadsheet
        #reference = StandardSheetReference()
        #sheet = self.get_current_tab_controller().findSheet(reference)
        #(row, col) = sheet.getFreeCell()
        #sheet.tabWidget.setCurrentWidget(sheet)
        #sheet.setCellByWidget(row, col, widget)



        #from .vtk_classes import QCDATWidget
        #widget = QCDATWidget()
        #sheet.setCellByWidget(row, col, widget)

        # Example getting canvas for first cell in current spreadsheet
        canvas = self.getCanvas(0,0)

        # Example uses the corresponding cel widget
        # this shoud not be neccecary if storing this info externally
        # Get first cell in active sheet
        reference = StandardSheetReference()
        sheet = self.get_current_tab_controller().findSheet(reference)
        cell = sheet.getCell(0,0)

        # Set up data and plot
        import cdms2, vcs
        cdmsfile = cdms2.open('/usr/local/uvcdat/2.2.0/sample_data/clt.nc')
        var = clt = cdmsfile('clt')
        cgm = gmBoxfill = vcs.getboxfill('default')

        #widget.updateContents(clt, gmBoxfill)

        # Draw plot on canvas
        canvas.clear()
        cell.extraDimsNames=var.getAxisIds()[:-2]
        cell.extraDimsIndex=[0,]*len(cell.extraDimsNames)
        cell.extraDimsLen=var.shape[:-2]
        #if hasattr(self.parent(),"toolBar"):
        #    t = self.parent().toolBar
        #    if hasattr(t,"dimSelector"):
        #        while (t.dimSelector.count()>0):
        #            t.dimSelector.removeItem(0)
        #        t.dimSelector.addItems(self.extraDimsNames)
        # Plot
        cmd = "#Now plotting\nvcs_canvas[%i].plot(" % (canvas.canvasid()-1)
        k1 = cell.prepExtraDims(var)
        args = [var(**k1)]
        cmd+="%s(**%s), " % (args[0].id,str(k1))
        kwargs = {}
        file_path = None
        #for fname in [ var.file, var.filename ]:
        #    if fname and ( os.path.isfile(fname) or fname.startswith('http://') ):
        #        file_path = fname
        #        break
        #if not file_path and var.url:
        #    file_path = var.url
        #if file_path: kwargs['cdmsfile'] =  file_path
        #record commands
        for k in kwargs:
            cmd+=", %s=%s" % (k, repr(kwargs[k]))
        cmd+=")"

        canvas.plot(cgm,*args,**kwargs)

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

    def prepareReviewingMode(self, vCol):
        """ Trim down most of the spreadsheet window """
        self.menuBar().hide()
        self.statusBar().hide()
        self.tabController.tabBar().hide()
        self.tabController.clearTabs()
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Pipeline Review - VisTrails Spreadsheet')
        self.resize(560*vCol, 512)
        self.show()

    def startReviewingMode(self):
        """ startReviewingMode()
        Reorganize the spreadsheet to contain only cells executed from locator:version

        """
        currentTab = self.tabController.currentWidget()
        if currentTab:
            currentTab.toolBar.hide()
            buttonLayout = QtGui.QHBoxLayout()
            buttons = [QtGui.QPushButton('&Accept'),
                       QtGui.QPushButton('&Discard')]
            buttonLayout.addStretch()
            buttonLayout.addWidget(buttons[0])
            buttonLayout.addWidget(buttons[1])
            buttonLayout.addStretch()
            currentTab.layout().addLayout(buttonLayout)
            self.connect(buttons[0], QtCore.SIGNAL('clicked()'),
                         self.acceptReview)
            self.connect(buttons[1], QtCore.SIGNAL('clicked()'),
                         self.discardReview)

    def discardReview(self):
        """ Just quit the program """
        QtCore.QCoreApplication.quit()

    def acceptReview(self):
        """ Copy image of all cells to the clipboard and then exit """
        currentTab = self.tabController.currentWidget()
        height = 0
        width = 0
        pixmaps = []
        version = -1
        if currentTab:
            (rCount, cCount) = currentTab.getDimension()
            for r in xrange(rCount):
                for c in xrange(cCount):
                    widget = currentTab.getCell(r, c)
                    if widget:
                        version = currentTab.getCellPipelineInfo(r, c)[0]['version']
                        pix = widget.grabWindowPixmap()
                        pixmaps.append(pix)
                        width += pix.width()
                        height = max(height, pix.height())
        finalImage = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(finalImage)
        x = 0
        for pix in pixmaps:
            painter.drawPixmap(x, 0, pix)
            x += pix.width()
        painter.end()
        filename = tempfile.gettempdir() + '/' + 'vtexport.png'
        finalImage.save(filename, 'PNG')
        sm = QtCore.QSharedMemory('VisTrailsPipelineImage')
        sm.create(32768)
        sm.attach()
        sm.lock()
        pfn = ctypes.c_char_p(filename)
        ctypes.memmove(int(sm.data()), pfn, len(filename))
        pfn = ctypes.c_char_p(str(version))
        ctypes.memmove(int(sm.data())+256, pfn, len(str(version)))
        sm.unlock()
        sm.detach()
        QtCore.QCoreApplication.quit()


    def changeTabController(self, name):
        self.tabControllerStack.change_selected_view(name)

    def addTabController(self, name):
        self.tabControllerStack.add_view(name)

    def removeTabController(self, name):
        self.tabControllerStack.remove_view(name)

    def getTabController(self, name):
        return self.tabControllerStack.get_tab_controller_by_name(name)

    def getCanvas(self, row=0, col=0):
        # return canvas for specified position in current sheet
        reference = StandardSheetReference()
        sheet = self.get_current_tab_controller().findSheet(reference)
        cell = sheet.getCell(row, col)
        return cell.canvas

    def getSelectedLocations(self):
        # return canvas for specified position in current sheet
        reference = StandardSheetReference()
        sheet = self.get_current_tab_controller().findSheet(reference)
        return sheet.getSelectedLocations()
