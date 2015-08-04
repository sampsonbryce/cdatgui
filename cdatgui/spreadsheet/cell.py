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
            pixmap.save(filename, 'PNG')
        elif ext == '.pdf':
            self.saveToPDF(filename)
        else:
            pixmap.save(filename)

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
        if cell.has_file_output_mode():
            modes = cell.get_file_output_modes()
            formats = []
            format_map = {}
            for mode in modes:
                for m_format in mode.get_formats():
                    if m_format not in format_map:
                        formats.append(m_format)
                        format_map[m_format] = mode
            selected_filter = None
            if cell.get_conf_file_format() is not None:
                selected_filter = '(*.%s)' % cell.get_conf_file_format()
            (filename, save_format) = \
                    QtGui.QFileDialog.getSaveFileNameAndFilter(
                        self, "Select a File to Export the Cell",
                        ".", ';;'.join(['(*.%s)' % f for f in formats]),
                        selected_filter)
            if filename:
                save_mode = format_map[save_format[3:-1]]
                cell.save_via_file_output(filename, save_mode)
        else:
            if not cell.save_formats:
                QtGui.QMessageBox.information(
                        self, "Export cell",
                        "This cell type doesn't provide any export option")
                return
            filename = QtGui.QFileDialog.getSaveFileName(
                self, "Select a File to Export the Cell",
                ".", ';;'.join(cell.save_formats))
            if filename:
                cell.dumpToFile(filename)

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
        info = self.sheet.getCellPipelineInfo(self.row, self.col)
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


class QCellPresenter(QtGui.QLabel):
    """
    QCellPresenter represents a cell in the Editing Mode. It has an
    info bar on top and control dragable icons on the bottom

    """
    def __init__(self, parent=None):
        """ QCellPresenter(parent: QWidget) -> QCellPresenter
        Create the layout of the widget

        """
        QtGui.QLabel.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.cellWidget = None

        layout = QtGui.QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(*([self.margin()]*4))
        layout.setRowStretch(1, 1)
        self.setLayout(layout)

        self.info = QPipelineInfo()
        layout.addWidget(self.info, 0, 0, 1, 2)

        self.manipulator = QCellManipulator()
        layout.addWidget(self.manipulator, 1, 0, 1, 2)

    def assignCellWidget(self, cellWidget):
        """ updateFromCellWidget(cellWidget: QWidget) -> None
        Assign a cell widget to this presenter

        """
        self.cellWidget = cellWidget
        if cellWidget:
            if hasattr(cellWidget, 'grabWindowPixmap'):
                bgPixmap = cellWidget.grabWindowPixmap()
            else:
                bgPixmap = QtGui.QPixmap.grabWidget(cellWidget)
            self.info.show()
        else:
            self.info.hide()
            bgPixmap = QtGui.QPixmap.grabWidget(self)
        self.thumbnail = QtGui.QPixmap(bgPixmap)
        painter = QtGui.QPainter(bgPixmap)
        painter.fillRect(bgPixmap.rect(),
                         QtGui.QBrush(QtGui.QColor(175, 198, 229, 196)))
        painter.end()
        self.setPixmap(bgPixmap)

    def assignCell(self, sheet, row, col):
        """ assignCell(sheet: Sheet, row: int, col: int) -> None
        Assign a sheet cell to the presenter

        """
        self.manipulator.assignCell(sheet, row, col)
        self.assignCellWidget(sheet.getCell(row, col))
        info = sheet.getCellPipelineInfo(row, col)
        self.info.updateInfo(info)

    def releaseCellWidget(self):
        """ releaseCellWidget() -> QWidget
        Return the ownership of self.cellWidget to the caller

        """
        cellWidget = self.cellWidget
        self.assignCellWidget(None)
        self.manipulator.assignCell(None, -1, -1)
        if cellWidget:
            cellWidget.setParent(None)
        return cellWidget

    def deleteLater(self):
        """ deleteLater() -> None
        Make sure to delete the cell widget if it exists

        """
        if (self.cellWidget):
            self.cellWidget.deleteLater()
        QtGui.QLabel.deleteLater(self)


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


class QPipelineInfo(QtGui.QFrame):
    """
    QPipelineInfo displays information about the executed pipeline of
    a cell. It has 3 static lines: Vistrail name, (pipeline name,
    pipeline id) and the cell type

    """
    def __init__(self, parent=None):
        """ QPipelineInfo(parent: QWidget) -> None
        Create the 3 information lines

        """
        QtGui.QFrame.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)

        pal = QtGui.QPalette(self.palette())
        color = QtGui.QColor(pal.brush(QtGui.QPalette.Base).color())
        color.setAlpha(196)
        pal.setBrush(QtGui.QPalette.Base, QtGui.QBrush(color))
        self.setPalette(pal)

        topLayout = QtGui.QVBoxLayout(self)
        topLayout.setSpacing(0)
        topLayout.setContentsMargins(0,0,0,0)
        self.setLayout(topLayout)

        hLine = QtGui.QFrame()
        hLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        hLine.setFixedHeight(1)
        topLayout.addWidget(hLine)

        layout = QtGui.QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(2,2,2,2)
        topLayout.addLayout(layout)

        self.edits = []
        texts = ['Vistrail', 'Index', 'Created by']
        for i in xrange(len(texts)):
            label = QInfoLabel(texts[i])
            layout.addWidget(label, i, 0, 1, 1)
            edit = QInfoLineEdit()
            self.edits.append(edit)
            layout.addWidget(edit, i, 1, 1, 1)

        topLayout.addStretch()
        hLine = QtGui.QFrame()
        hLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        hLine.setFixedHeight(1)
        topLayout.addWidget(hLine)

    def updateInfo(self, info):
        """ updateInfo(info: (dict, pid)) -> None
        Update the information of a pipeline info

        """
        if info!=None and info[0]['locator']!=None:
            self.edits[0].setText(str(info[0]['locator'].name))
            self.edits[1].setText('(Pipeline: %d, Module: %d)'
                                  % (info[0]['version'], info[0]['moduleId']))
            self.edits[2].setText(str(info[0]['reason']))
        else:
            for edit in self.edits:
                edit.setText('N/A')


class QCellManipulator(QtGui.QFrame):
    """
    QCellManipulator contains several dragable icons that allow users
    to move/copy or perform some operation from one cell to
    another. It also inclues a button for update the pipeline under
    the cell to be a new version on the pipeline. It is useful for the
    parameter exploration talks back to the builder

    """
    def __init__(self, parent=None):
        """ QPipelineInfo(parent: QWidget) -> None
        Create the 3 information lines

        """
        QtGui.QFrame.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        layout.addStretch()

        bLayout = QtGui.QHBoxLayout()
        layout.addLayout(bLayout)

        bInfo = [(':/images/copy_cell.png',
                  'Drag to copy this cell to another place',
                  'copy', 'Copy'),
                 (':/images/move_cell.png',
                  'Drag to move this cell to another place',
                  'move', 'Move'),]

        self.buttons = []

        bLayout.addStretch()
        for b in bInfo:
            button = QCellDragLabel(QtGui.QPixmap(b[0]))
            button.setToolTip(b[1])
            button.setStatusTip(b[1])
            button.action = b[2]
            vLayout = QtGui.QVBoxLayout()
            vLayout.addWidget(button)
            label = QtGui.QLabel(b[3])
            label.setAlignment(QtCore.Qt.AlignCenter)
            vLayout.addWidget(label)
            bLayout.addLayout(vLayout)
            self.buttons.append(button)
            self.buttons.append(label)

        uLayout = QtGui.QHBoxLayout()
        uLayout.addStretch()
        layout.addLayout(uLayout)

        bLayout.addStretch()

        layout.addStretch()

        self.innerRubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle,
                                                 self)

    def assignCell(self, sheet, row, col):
        """ assignCell(sheet: Sheet, row: int, col: int) -> None
        Assign a cell to the manipulator, so it knows where to drag
        and drop

        """
        self.cellInfo = (sheet, row, col)
        for b in self.buttons:
            if hasattr(b, 'updateCellInfo'):
                b.updateCellInfo(self.cellInfo)
            if sheet and sheet.getCell(row, col)!=None:
                widget = sheet.getCell(row, col)
                b.setVisible(not isinstance(widget, QCellPresenter) or
                             widget.cellWidget is not None)
            else:
                b.setVisible(False)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the other cell info

        """
        mimeData = event.mimeData()
        if hasattr(mimeData, 'cellInfo'):
            if (mimeData.cellInfo==self.cellInfo or
                mimeData.cellInfo[0]==None or
                self.cellInfo[0]==None):
                event.ignore()
            else:
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
                self.highlight()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """ dragLeaveEvent(event: QDragLeaveEvent) -> None
        Unhighlight when the cursor leaves

        """
        self.highlight(False)

    def dropEvent(self, event):
        """ dragLeaveEvent(event: QDragLeaveEvent) -> None
        Unhighlight when the cursor leaves

        """
        self.highlight(False)
        mimeData = event.mimeData()
        action = mimeData.action
        cellInfo = mimeData.cellInfo
        manipulator = mimeData.manipulator
        if action in ['move', 'copy']:
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()

            if action=='move':
                self.cellInfo[0].swapCell(self.cellInfo[1], self.cellInfo[2],
                                          cellInfo[0], cellInfo[1], cellInfo[2])
                manipulator.assignCell(*self.cellInfo)
                self.assignCell(*cellInfo)

            if action=='copy':
                cellInfo[0].copyCell(cellInfo[1], cellInfo[2],
                                     self.cellInfo[0], self.cellInfo[1],
                                     self.cellInfo[2])

        else:
            event.ignore()


    def highlight(self, on=True):
        """ highlight(on: bool) -> None
        Highlight the cell as if being selected

        """
        if on:
            self.innerRubberBand.setGeometry(self.rect())
            self.innerRubberBand.show()
        else:
            self.innerRubberBand.hide()


class QCellDragLabel(QtGui.QLabel):
    """
    QCellDragLabel is a pixmap label allowing users to drag it to
    another cell manipulator

    """
    def __init__(self, pixmap, parent=None):
        """ QCellDragLabel(pixmap: QPixmap, parent: QWidget) -> QCellDragLabel
        Construct the pixmap label

        """
        QtGui.QLabel.__init__(self, parent)
        self.setMargin(0)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setFixedSize(64, 64)
        self.cursorPixmap = pixmap.scaled(self.size())

        self.startPos = None
        self.cellInfo = (None, -1, -1)
        self.action = None

    def updateCellInfo(self, cellInfo):
        """ updateCellInfo(cellInfo: tuple) -> None
        Update cellInfo for mime data while dragging

        """
        self.cellInfo = cellInfo

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Store the start position for drag event

        """
        self.startPos = QtCore.QPoint(event.pos())
        QtGui.QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(event: QMouseEvent) -> None
        Prepare to drag

        """
        p = event.pos() - self.startPos
        if p.manhattanLength()>=QtGui.QApplication.startDragDistance():
            drag = QtGui.QDrag(self)
            data = QtCore.QMimeData()
            data.cellInfo = self.cellInfo
            data.action = self.action
            data.manipulator = self.parent()
            drag.setMimeData(data)
            drag.setHotSpot(self.cursorPixmap.rect().center())
            drag.setPixmap(self.cursorPixmap)
            drag.start(QtCore.Qt.MoveAction)
