from PySide import QtCore, QtGui
import math


class DynamicGridLayout(QtGui.QGridLayout):
    def __init__(self, col_width, parent=None):
        """
        col_width: width of the columns, therefore specifies how to distribute widgets.
                    col_width must be greater than the minimum width of widget or downsizing will fail
        """
        super(DynamicGridLayout, self).__init__()

        self.col_width = col_width
        self.cur_col_count = 1
        self.widgets = []
        self.counts = [0]

    def setGeometry(self, rect):
        self.buildGrid(rect)
        super(DynamicGridLayout, self).setGeometry(rect)

    def addNewWidgets(self, widgets):
        """preferred method of adding widgets, only has to call build grid once"""
        self.widgets.extend(widgets)
        self.buildGrid(self.geometry(), force=True)

    def addNewWidget(self, widget):
        self.widgets.append(widget)
        self.buildGrid(self.geometry(), force=True)

    def resizeEvent(self, ev):
        super(DynamicGridLayout, self).resizeEvent(ev)
        self.buildGrid()

    def setColumnWidth(self, width):
        self.col_width = width
        self.buildGrid(self.geometry(), force=True)

    def buildGrid(self, rect, force=False):

        possible_columns = rect.width() / self.col_width

        if not possible_columns:
            possible_columns = 1

        # bypasses check and rebuilds regardless
        if not force:
            if possible_columns == self.cur_col_count:
                return

        # clearing
        self.clearWidgets()

        # calculate
        full_columns = possible_columns - 1
        num_items = len(self.widgets)
        row_height = 0

        iterator = iter(self.widgets)
        columns = []

        while num_items > row_height:
            for col in range(full_columns):
                if not num_items:
                    break
                if len(columns) - 1 < col:
                    columns.append(0)
                columns[col] += 1
                num_items -= 1
            row_height += 1

        columns.append(num_items)

        for col, row_count in enumerate(columns):
            for row in range(row_count):
                self.addWidget(iterator.next(), row, col)

        self.cur_col_count = possible_columns

    def clearWidgets(self):
        """Clears widgets from the grid layout. Does not delete widgets"""
        for col, row_count in enumerate(self.counts):
            if row_count:
                for row in range(row_count):
                    cur_item = self.grid.itemAtPosition(row, col).widget()
                    self.grid.removeWidget(cur_item)
                    self.counts[col] -= 1
                    assert self.counts[col] >= 0
        while len(self.counts) != 1:
            self.counts.pop(-1)

    def getWidgets(self):
        return self.widgets

    def removeWidget(self, widget):
        """Removes widgets from gridlayout and updates list and counts
            Does Not Delete Widget
        """
        for i in self.widgets:
            if i == widget:

                # update counts
                for col, row_count in enumerate(self.counts):
                    if row_count:
                        for row in range(row_count):
                            cur_item = self.grid.itemAtPosition(row, col).widget()
                            if cur_item == widget:
                                self.counts[col] -= 1

                self.widgets.remove(i)
                self.buildGrid(self.geometry(), force=True)
                return


if __name__ == "__main__":
    app = QtGui.QApplication([])

    flow = DynamicGridLayout(300)
    widgets = []
    for i in range(100):
        w = QtGui.QWidget()
        h = QtGui.QHBoxLayout()
        h.addWidget(QtGui.QLabel("Test %d" % i))
        h.addWidget(QtGui.QPushButton("Button %d" % i))
        w.setLayout(h)
        widgets.append(w)
    flow.addNewWidgets(widgets)
    win = QtGui.QWidget()
    win.setLayout(flow)
    win.show()
    win.raise_()
    app.exec_()
