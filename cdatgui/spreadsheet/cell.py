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

"""This file contains classes working with cell helper widgets, i.e. toolbar,
esizer, etc.:
  QCellWidget
  QCellToolBar
"""

from __future__ import division

import datetime
import os
from PySide import QtCore, QtGui
import tempfile

import cell_rc
import celltoolbar_rc


class QCellWidget(QtGui.QWidget):
    """
    QCellWidget is the base cell class. All types of spreadsheet cells
    should inherit from this.

    """
    save_formats = ["Images (*.png *.xpm *.jpg)",
                    "Portable Document Format (*.pdf)"]

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        """ QCellWidget(parent: QWidget) -> QCellWidget
        Instantiate the cell and helper properties

        """
        QtGui.QWidget.__init__(self, parent, flags)
        # cell can be captured if it re-implements saveToPNG
        self._capturingEnabled = (not isinstance(self, QCellWidget) and
                                  hasattr(self, 'saveToPNG'))
        # For thumbnail comparison testing
        #if configuration.fixedCellSize:
        #    self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        #    self.setFixedSize(200, 180)

    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> Bool
        Abtract function for saving the current widget contents to an
        image file
        Returns True when succesful

        """
        debug.critical('saveToPNG() is unimplemented by the inherited cell')

    def deleteLater(self):
        """ deleteLater() -> None
        Make sure to clear history and delete the widget

        """
        QtGui.QWidget.deleteLater(self)

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple)
        Make sure to capture to history

        """
        # Capture window into history for playback
        pass

    def resizeEvent(self, e):
        """ resizeEvent(e: QEvent) -> None
        Re-adjust the player widget

        """
        QtGui.QWidget.resizeEvent(self, e)

    def grabWindowPixmap(self):
        """ grabWindowPixmap() -> QPixmap
        Widget special grabbing function

        """
        return QtGui.QPixmap.grabWidget(self)

    def dumpToFile(self, filename):
        """ dumpToFile(filename: str, dump_as_pdf: bool) -> None
        Dumps itself as an image to a file, calling grabWindowPixmap """
        pixmap = self.grabWindowPixmap()
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            pixmap.accept(filename, 'PNG')
        elif ext == '.pdf':
            self.saveToPDF(filename)
        else:
            pixmap.accept(filename)

    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        pixmap = self.grabWindowPixmap()
        size = pixmap.size()
        printer.setPaperSize(QtCore.QSizeF(size.width(), size.height()),
                             QtGui.QPrinter.Point)
        painter = QtGui.QPainter()
        painter.begin(printer)
        rect = painter.viewport()
        size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(pixmap.rect())
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

class QCellToolBar(QtGui.QToolBar):
    """
    CellToolBar is inherited from QToolBar with some functionalities
    for interacting with CellHelpers

    """
    def __init__(self, sheet):
        """ CellToolBar(sheet: SpreadsheetSheet) -> CellToolBar
        Initialize the cell toolbar by calling the user-defined
        toolbar construction function

        """
        QtGui.QToolBar.__init__(self,sheet)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.sheet = sheet
        self.row = -1
        self.col = -1
        self.layout().setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        pixmap = self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)
        self.addSaveCellAction()
        self.addExecuteCellAction()
        self.appendAction(QCellToolBarRemoveCell(QtGui.QIcon(pixmap), self))
        self.appendAction(QCellToolBarMergeCells(QtGui.QIcon(':celltoolbar/mergecells.png'), self))
        self.createToolBar()

    def addSaveCellAction(self):
        if not hasattr(self, 'saveActionVar'):
            self.saveActionVar = QCellToolBarSelectedCell(
                    QtGui.QIcon(":/images/camera.png"),
                    "Save cell",
                    self)
            self.saveActionVar.setStatusTip("Export this cell only")

            self.connect(self.saveActionVar, QtCore.SIGNAL('triggered(bool)'),
                         self.exportCell)
        self.appendAction(self.saveActionVar)

    def exportCell(self, checked=False):
        cell = self.sheet.getCell(self.row, self.col)

    def addExecuteCellAction(self):
        if not hasattr(self, 'executeActionVar'):
            self.executeActionVar = QCellToolBarSelectedCell(
                    QtGui.QIcon(":/images/view-refresh.png"),
                    "Re-execute cell",
                    self)
            self.executeActionVar.setStatusTip("Re-execute this cell")

            self.connect(self.executeActionVar, QtCore.SIGNAL('triggered(bool)'),
                         self.executeCell)
        self.appendAction(self.executeActionVar)

    def executeCell(self, checked=False):
        pass



    def createToolBar(self):
        """ createToolBar() -> None
        A user-defined method for customizing the toolbar. This is
        going to be an empty method here for inherited classes to
        override.

        """
        pass

    def snapTo(self, row, col):
        """ snapTo(row, col) -> None
        Assign which row and column the toolbar should be snapped to

        """
        self.row = row
        self.col = col
        self.updateToolBar()

    def updateToolBar(self):
        """ updateToolBar() -> None
        This will get called when the toolbar widgets need to have
        their status updated. It sends out needUpdateStatus signal
        to let the widget have a change to update their own status

        """
        cellWidget = self.sheet.getCell(self.row, self.col)
        for action in self.actions():
            action.needUpdateStatus.emit((self.sheet, self.row, self.col,
                                          cellWidget))

    def connectAction(self, action, widget):
        """ connectAction(action: QAction, widget: QWidget) -> None
        Connect actions to special slots of a widget

        """
        if hasattr(widget, 'updateStatus'):
            action.needUpdateStatus.connect(widget.updateStatus)
        if hasattr(widget, 'triggeredSlot'):
            action.triggered.connect(widget.triggeredSlot)
        if hasattr(widget, 'toggledSlot'):
            action.toggled.connect(widget.toggledSlot)

    def appendAction(self, action):
        """ appendAction(action: QAction) -> QAction
        Setup and add action to the tool bar

        """
        action.toolBar = self
        self.addAction(action)
        self.connectAction(action, action)
        return action

    def appendWidget(self, widget):
        """ appendWidget(widget: QWidget) -> QAction
        Setup the widget as an action and add it to the tool bar

        """
        action = self.addWidget(widget)
        widget.toolBar = self
        action.toolBar = self
        self.connectAction(action, widget)
        return action

    def getSnappedWidget(self):
        """ getSnappedWidget() -> QWidget
        Return the widget being snapped by the toolbar

        """
        if self.row>=0 and self.col>=0:
            return self.sheet.getCell(self.row, self.col)
        else:
            return None

class CellToolbarAction(QtGui.QAction):
    needUpdateStatus = QtCore.Signal(tuple)


class QCellToolBarSelectedCell(CellToolbarAction):
    """
    QCellToolBarSelectedCell is an action only visible if the cell isn't empty.
    """
    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info

        """
        (sheet, row, col, cellWidget) = info
        self.setVisible(cellWidget is not None)


class QCellToolBarRemoveCell(QCellToolBarSelectedCell):
    """
    QCellToolBarRemoveCell is the action to clear the current cell

    """
    def __init__(self, icon, parent=None):
        """ QCellToolBarRemoveCell(icon: QIcon, parent: QWidget)
                                   -> QCellToolBarRemoveCell
        Setup the image, status tip, etc. of the action

        """
        QCellToolBarSelectedCell.__init__(self,
                                          icon,
                                          "&Clear the current cell",
                                          parent)
        self.setStatusTip("Clear the current cell")

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked

        """
        cellWidget = self.toolBar.getSnappedWidget()
        r = QtGui.QMessageBox.question(cellWidget, 'Clear cell',
                                       'Are you sure to clear the cell?',
                                       QtGui.QMessageBox.Yes |
                                       QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No)
        if (r==QtGui.QMessageBox.Yes):
            self.toolBar.sheet.deleteCell(self.toolBar.row, self.toolBar.col)


class QCellToolBarMergeCells(CellToolbarAction):
    """
    QCellToolBarMergeCells is the action to merge selected cells to a
    single cell if they are in consecutive poisitions

    """
    def __init__(self, icon, parent=None):
        """ QCellToolBarMergeCells(icon: QIcon, parent: QWidget)
                                   -> QCellToolBarMergeCells
        Setup the image, status tip, etc. of the action

        """
        QtGui.QAction.__init__(self,
                               icon,
                               "&Merge cells",
                               parent)
        self.setStatusTip("Merge selected cells to a single cell if "
                          "they are in consecutive poisitions")
        self.setCheckable(True)

    def triggeredSlot(self):
        """ toggledSlot() -> None
        Execute the action when the button is clicked

        """
        # Merge
        if self.isChecked():
            sheet = self.toolBar.sheet
            selectedCells = sorted(sheet.getSelectedLocations())
            topLeft = selectedCells[0]
            bottomRight = selectedCells[-1]
            sheet.setSpan(topLeft[0], topLeft[1],
                          bottomRight[0]-topLeft[0]+1,
                          bottomRight[1]-topLeft[1]+1)
        else:
            sheet = self.toolBar.sheet
            selectedCells = sorted(sheet.getSelectedLocations())
            for (row, col) in selectedCells:
                sheet.setSpan(row, col, 1, 1)
        sheet.clearSelection()
        self.toolBar.updateToolBar()

    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info

        """
        (sheet, row, col, cellWidget) = info
        selectedCells = sorted(sheet.getSelectedLocations())

        # Will not show up if there is no cell selected
        if len(selectedCells)==0:
            self.setVisible(False)

        # If there is a single cell selected, only show up if it has
        # been merged before so that user can un-merge cells
        elif len(selectedCells)==1:
            showUp = False
            if selectedCells[0]==(row, col):
                span = sheet.getSpan(row, col)
                if span[0]>1 or span[1]>1:
                    showUp = True
            if showUp:
                self.setChecked(True)
                self.setVisible(True)
            else:
                self.setVisible(False)

        # If there are multiple cells selected, only show up if they
        # can be merged, i.e. cells are in consecutive position and
        # none of them is already merged
        else:
            showUp = False
            validRange = False
            topLeft = selectedCells[0]
            bottomRight = selectedCells[-1]
            fullCount = (bottomRight[0]-topLeft[0]+1)*(bottomRight[1]-topLeft[1]+1)
            validRange = len(selectedCells)==fullCount
            if validRange:
                showUp = True
                for (r, c) in selectedCells:
                    span = sheet.getSpan(r, c)
                    if span[0]>1 or span[1]>1:
                        showUp = False
                        break
            if showUp:
                self.setChecked(False)
                self.setVisible(True)
            else:
                self.setVisible(False)


class QCellContainer(QtGui.QWidget):
    """ QCellContainer is a simple QWidget containing the actual cell
    widget as a child. This also acts as a sentinel protecting the
    actual cell widget from being destroyed by sheet widgets
    (e.g. QTableWidget) where they take control of the cell widget.

    """
    def __init__(self, widget=None, parent=None):
        """ QCellContainer(parent: QWidget) -> QCellContainer
        Create an empty container

        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.containedWidget = None
        self.setWidget(widget)
        self.toolBar = None

    def setWidget(self, widget):
        """ setWidget(widget: QWidget) -> None
        Set the contained widget of this container

        """
        if widget!=self.containedWidget:
            if self.containedWidget:
                self.layout().removeWidget(self.containedWidget)
                self.containedWidget.deleteLater()
                self.toolBar = None
            if widget:
                widget.setParent(self)
                self.layout().addWidget(widget)
                widget.show()
            self.containedWidget = widget

    def widget(self):
        """ widget() -> QWidget
        Return the contained widget

        """
        return self.containedWidget

    def takeWidget(self):
        """ widget() -> QWidget
        Take the contained widget out without deleting

        """
        widget = self.containedWidget
        if self.containedWidget:
            self.layout().removeWidget(self.containedWidget)
            self.containedWidget.setParent(None)
            self.containedWidget = None
        self.toolBar = None
        return widget


class QInfoLineEdit(QtGui.QLineEdit):
    """
    QInfoLineEdit is wrapper for a transparent, un-frame, read-only
    line edit

    """
    def __init__(self, parent=None):
        """ QInfoLineEdit(parent: QWidget) -> QInfoLineEdit
        Initialize the line edit

        """
        QtGui.QLineEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setFrame(False)
        pal = QtGui.QPalette(self.palette())
        pal.setBrush(QtGui.QPalette.Base,
                     QtGui.QBrush(QtCore.Qt.NoBrush))
        self.setPalette(pal)


class QInfoLabel(QtGui.QLabel):
    """
    QInfoLabel is wrapper for a transparent, bolded label

    """
    def __init__(self, text='', parent=None):
        """ QInfoLabel(text: str, parent: QWidget) -> QInfoLabel
        Initialize the line edit

        """
        QtGui.QLabel.__init__(self, text, parent)
        font = QtGui.QFont(self.font())
        font.setBold(True)
        self.setFont(font)
