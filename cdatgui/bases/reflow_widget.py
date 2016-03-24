from PySide import QtCore, QtGui


class ReflowWidget(QtGui.QWidget):
    def __init__(self, col_width, parent=None):
        """
        col_width: width of the columns, therefore specifies how to distribute widgets.
                    col_width must be greater than the minimum width of widget or downsizing will fail
        """
        super(ReflowWidget, self).__init__()

        self.col_width = col_width
        self.cur_col_count = 1
        self.widgets = []
        self.grid = QtGui.QGridLayout()
        self.counts = [0]

        self.setLayout(self.grid)

    def addWidgets(self, widgets):
        """preferred method of adding widgets, only has to call build grid once"""
        self.widgets.extend(widgets)
        self.buildGrid(True)

    def addWidget(self, widget):
        self.widgets.append(widget)
        self.buildGrid(True)

    def resizeEvent(self, ev):
        print "resizing, width=", self.width()
        super(ReflowWidget, self).resizeEvent(ev)
        self.buildGrid()

    def setColumnWidth(self, width):
        self.col_width = width

    def buildGrid(self, force=False):
        print "building grid"
        possible_columns = self.width() / self.col_width
        if not possible_columns:
            possible_columns = 1

        # bypasses check and rebuilds regardless
        if not force:
            if possible_columns == self.cur_col_count:
                return

        # clearing
        self.clearWidget()

        # build
        try:
            sec_length = len(self.widgets) / possible_columns
        except ZeroDivisionError:
            sec_length = len(self.widgets)
        leftover = len(self.widgets) - (sec_length * possible_columns)
        iterator = iter(self.widgets)

        while possible_columns < len(self.counts):
            self.counts.pop(-1)

        for sec in range(possible_columns):
            for row in range(sec_length):
                self.grid.addWidget(iterator.next(), row, sec)

                # if new column, track counts
                if len(self.counts) - 1 < sec:
                    self.counts.append(0)
                self.counts[sec] += 1

            if leftover:
                n_widget = iterator.next()
                self.grid.addWidget(n_widget, sec_length, sec)
                leftover -= 1

            self.cur_col_count = possible_columns

    def clearWidget(self):
        """clears widgets from the grid layout. Does not delete widgets"""
        print "clearing, counts =", self.counts
        print "len counts", len(self.counts)
        for col, row_count in enumerate(self.counts):
            print "COL, row_count:", col, row_count
            if row_count:
                for row in range(row_count):
                    cur_item = self.grid.itemAtPosition(row, col).widget()
                    self.grid.removeWidget(cur_item)
                    self.counts[col] -= 1
                    assert self.counts[col] >= 0
        print "COUNTS AFTER CLEAR:", self.counts

    def getWidgets(self):
        return self.widgets

    def removeWidget(self, widget):
        """removes widgets from gridlayout and updates list and counts"""
        for i in self.widgets:
            if i == widget:

                # update counts
                print "COUNTS", self.counts
                for col, row_count in enumerate(self.counts):
                    if row_count:
                        for row in range(row_count):
                            print "ROW, COLUMN:", row, col
                            cur_item = self.grid.itemAtPosition(row, col).widget()
                            if cur_item == widget:
                                self.counts[col] -= 1

                self.widgets.remove(i)
                self.buildGrid(True)
                return


if __name__ == "__main__":
    app = QtGui.QApplication([])

    flow = ReflowWidget(300)
    widgets = []
    for i in range(100):
        w = QtGui.QWidget()
        h = QtGui.QHBoxLayout()
        h.addWidget(QtGui.QLabel("Test %d" % i))
        h.addWidget(QtGui.QPushButton("Button %d" % i))
        w.setLayout(h)
        widgets.append(w)
    flow.addWidgets(widgets)
    flow.show()
    flow.raise_()
    app.exec_()
