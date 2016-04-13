from PySide import QtGui, QtCore


class GridCell(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GridCell, self).__init__(parent)
        self.label = QtGui.QLabel(parent=self)

    def update(self, model, index):
        """
        Update contents of cell to reflect model item, and return
        cell minimum dimensions
        """
        self.label.setText(model.data(index, QtCore.Qt.DisplayRole))


def fixed_size():
    return QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)


class GridView(QtGui.QAbstractItemView):
    def __init__(self, col_width=200, row_height=200, cell_type=GridCell, parent=None):
        super(GridView, self).__init__(parent)
        self.grid = QtGui.QGridLayout()

        self.display_child = QtGui.QWidget()
        self.display_child.setSizePolicy(fixed_size())

        self.setViewport(self.display_child)
        self.display_child.setLayout(self.grid)
        self.grid.setSizeConstraint(QtGui.QLayout.SetMaximumSize)

        self.resizing = False
        self.__column_cache = 0
        self.cell_width = col_width
        self.row_height = row_height
        self.cell_type = cell_type
        self.cells = []
        self.horizontalScrollBar().valueChanged.connect(self.alignWidget)
        self.verticalScrollBar().valueChanged.connect(self.alignWidget)

    def alignWidget(self, *args):
        pos = self.display_child.rect().topLeft()
        hval = self.horizontalScrollBar().value()
        vval = self.verticalScrollBar().value()
        self.display_child.move(pos.x() - hval, pos.y() - vval)

    def setModel(self, model):
        if model != self.model():
            # Need to check the comparitive lengths to see
            # if we need more or fewer cells
            if self.model() is not None and model.rowCount() < self.model().rowCount():
                for cell in self.cells[model.rowCount():]:
                    cell.deleteLater()
                self.cells = self.cells[:model.rowCount()]
            super(GridView, self).setModel(model)
            self.rowsInserted(QtCore.QModelIndex(), 0, model.rowCount())

    def columns(self):
        return max(1, self.width() / self.cell_width)

    def rows(self):
        return max(1, len(self.cells) / self.columns())

    def col(self, index):
        return self.cells[index::self.columns()]

    def updateLayout(self):
        cols = self.columns()
        self.__column_cache = cols

        for ind, cell in enumerate(self.cells):
            self.grid.takeAt(ind)
        for ind, cell in enumerate(self.cells):
            row, col = ind / cols, ind % cols
            self.grid.addWidget(cell, row, col)
        self.display_child.setMaximumHeight(self.row_height * self.rows())

    def rowsInserted(self, parent, start, end):
        length = end - start
        offset = len(self.cells)
        cols = self.columns()

        num_rows = self.rows()

        # Add extra cells as necessary
        for i in range(length):
            cell = self.cell_type()
            row = (i + offset) / cols
            col = (i + offset) % cols

            self.cells.append(cell)
            self.grid.addWidget(cell, row, col)

        # Update all changed cells to have accurate data
        for index, cell in enumerate(self.cells[start:]):
            index += start
            pointer = self.model().index(index, 0)
            cell.update(self.model(), pointer)

        if self.__column_cache != self.columns():
            self.updateLayout()
        elif num_rows != self.rows():
                self.display_child.resize(self.width(), self.rows() * self.row_height)

    def el_rects(self):
        rects = []
        for el in self.cells:
            rects.append(QtCore.QRect(el.pos(), el.size()))
        return rects

    def setSelection(self, rect, flags):
        for ind, el_rect in enumerate(self.el_rects()):
            if el_rect.intersects(rect):
                break
        model_index = self.model().index(ind, 0)
        self.selectionModel().select(model_index, flags)

    def resizeEvent(self, event):
        super(GridView, self).resizeEvent(event)
        if self.columns() != self.__column_cache:
            self.updateLayout()
        self.horizontalScrollBar().setRange(0, self.display_child.width() - self.width())
        self.verticalScrollBar().setRange(0, self.display_child.height() - self.height())

    def horizontalOffset(self):
        print "horizontalOffset"
        return 0

    def verticalOffset(self):
        print "verticalOffset"
        return 0

    def indexAt(self, point):
        for ind, rect in enumerate(self.el_rects()):
            if rect.contains(point):
                break
        return self.model().index(ind, 0)

    def isIndexHidden(self, index):
        print "isIndexHidden"
        return False

    def visualRect(self, index):
        el = self.cells[index.row()]
        pos = el.pos()
        size = el.size()
        return QtCore.QRect(pos, size)

    def scrollTo(self, ind, hint=QtGui.QAbstractItemView.EnsureVisible):
        print "scrollTo"
        pass

    def moveCursor(self, cursorAction, modifiers):
        print "moveCursor"
        return self.model().index(0, 0)

    def dataChanged(self, top_left, bottom_right):
        print "dataChanged"
        pass

    def rowsAboutToBeRemoved(self, parent, start, end):
        print "rowsAboutToBeRemoved"
        pass

    def currentChanged(self, current, previous):
        print "currentChanged"
        pass

    def selectionChanged(self, selected, deselected):
        print "selectionChanged"
        pass


class LabeledImage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LabeledImage, self).__init__(parent)
        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        self.image_label = QtGui.QLabel()
        l.addWidget(self.image_label)
        self.text_label = QtGui.QLabel()
        l.addWidget(self.text_label)

    def set_image(self, image):
        self.image_label.setPixmap(image)
        self.setMinimumWidth(image.width())

    def set_title(self, text):
        self.text_label.setText(text)

