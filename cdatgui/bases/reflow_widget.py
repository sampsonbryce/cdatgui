from PySide import QtCore, QtGui


class ReflowWidget(QtGui.QWidget):
    def __init__(self, col_width, parent=None):
        super(ReflowWidget, self).__init__()

        self.col_width = col_width
        self.cur_col_count = 1
        self.widgets = []
        self.grid = QtGui.QGridLayout()
        self.counts = [0]

        self.setLayout(self.grid)

    def addWidgets(self, widgets):
        self.widgets.extend(widgets)
        for row, widget in enumerate(widgets):
            self.grid.addWidget(widget, row, self.cur_col_count - 1)
            self.counts[self.cur_col_count - 1] += 1

    def addWidget(self, widget):
        self.widgets.append(widget)
        self.grid.addWidget(widget, self.counts[self.cur_col_count - 1], self.cur_col_count - 1)
        self.counts[self.cur_col_count - 1] += 1

    def resizeEvent(self, ev):
        print "resizing, width=", self.width()
        super(ReflowWidget, self).resizeEvent(ev)
        self.buildGrid()

    def setColumnWidth(self, width):
        self.col_width = width

    def buildGrid(self):
        print "building grid"
        possible_columns = self.width() / self.col_width
        if not possible_columns:
            possible_columns = 1

        if possible_columns and possible_columns != self.cur_col_count:
            self.clearWidget()
            try:
                sec_length = len(self.widgets) / possible_columns
            except ZeroDivisionError:
                sec_length = len(self.widgets)
            leftover = len(self.widgets) - (sec_length * possible_columns)
            iterator = iter(self.widgets)

            for sec in range(possible_columns):
                for row in range(sec_length):
                    self.grid.addWidget(iterator.next(), row, sec)

                    # if new column track counts
                    if len(self.counts) - 1 < sec:
                        self.counts.append(0)
                    self.counts[sec] += 1

                if leftover:
                    n_widget = iterator.next()
                    self.grid.addWidget(n_widget, sec_length, sec)
                    leftover -= 1

            self.cur_col_count = possible_columns

    def clearWidget(self):
        print "clearing"
        for item in self.counts:
            if item:
                for col in range(len(self.counts)):
                    for row in range(self.counts[col]):
                        cur_item = self.grid.itemAtPosition(row, col).widget()
                        self.grid.removeWidget(cur_item)
                        self.counts[col] -= 1
                        assert self.counts[col] >= 0
            break

    def getWidgets(self):
        return self.widgets


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
