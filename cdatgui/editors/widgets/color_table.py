from PySide import QtGui, QtCore
import vcs
from cdatgui.bases.background_delegate import BorderHighlightStyleDelegate


class ColormapTable(QtGui.QTableWidget):
    """Displays a selectable table of colors from a VCS colormap."""

    singleColorSelected = QtCore.Signal(object)

    def __init__(self, rows, parent=None):
        super(ColormapTable, self).__init__(rows, 256 / rows, parent=parent)
        self._cmap = None
        self._real_map = None
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        for ind in range(256):
            item = QtGui.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.setItem(ind / self.columnCount(), ind % self.columnCount(), item)
        for ind in range(rows):
            self.setRowHeight(ind, 32)
        for ind in range(self.columnCount()):
            self.setColumnWidth(ind, 32)
        self.setItemDelegate(BorderHighlightStyleDelegate())
        self.setStyleSheet("selection-background-color: rgba(0,0,0,0);")
        self.itemSelectionChanged.connect(self.update_selection)

    def get_cell(self, index):
        return self.cmap.index[index]

    def set_cell(self, index, r, g, b, a):
        self.cmap.index[index] = (r / 2.55, g / 2.55, b / 2.55, a / 2.55)
        self.update_table()

    def get_color_range(self):
        min_ind = 255
        max_ind = 0
        for sel in self.selectedRanges():
            start = self.row_col_to_ind(sel.topRow(), sel.leftColumn())
            end = self.row_col_to_ind(sel.bottomRow(), sel.rightColumn())
            if start < min_ind:
                min_ind = start
            if end > max_ind:
                max_ind = end
        return min_ind, max_ind

    def update_selection(self):
        ranges = self.selectedRanges()
        row_columns = {row: {col: False for col in range(self.columnCount())} for row in range(self.rowCount())}
        start_row = self.rowCount()
        end_row = 0
        # Coalesce the ranges
        for sel in ranges:
            start_row = min(sel.topRow(), start_row)
            end_row = max(sel.bottomRow(), end_row)
            for row in range(sel.topRow(), sel.bottomRow() + 1):
                cols = row_columns.get(row, {})
                for col in range(sel.leftColumn(), sel.rightColumn() + 1):
                    cols[col] = True
        
        if len(ranges) == 1 and sel.topRow() == sel.bottomRow() and sel.leftColumn() == sel.rightColumn():
            self.singleColorSelected.emit(self.row_col_to_ind(sel.topRow(), sel.leftColumn()))
            return
        else:
            self.singleColorSelected.emit(None)


        new_selections = []
        for row in range(start_row, end_row + 1):
            cols = sorted(row_columns[row].keys())
            missing_cols = []
            # rows should always be "started" after the first row
            started_row = row not in (start_row, end_row)
            for col in cols:
                if not row_columns[row][col]:
                    if started_row is False:
                        # First or last row, just keep going till we find the beginning
                        continue
                    else:
                        if row == end_row:
                            # Reached the end, we're done
                            break
                        missing_cols.append(col)
                else:
                    if started_row is False:
                        started_row = True
                        if row == end_row and end_row != start_row:
                            missing_cols.extend(range(0, col))
            if missing_cols:
                new_selection = QtGui.QTableWidgetSelectionRange(row, min(missing_cols), row, max(missing_cols))
                new_selections.append(new_selection)

        if new_selections:
            self.blockSignals(True)
            for sel in new_selections[:-1]:
                self.setRangeSelected(sel, True)
            self.blockSignals(False)
            self.setRangeSelected(new_selections[-1], True)

    def row_col_to_ind(self, row, col):
        return row * self.columnCount() + col

    def ind_to_row_col(self, index):
        return index / self.columnCount(), index % self.columnCount()

    @property
    def cmap(self):
        return self._cmap
    
    @cmap.setter
    def cmap(self, value):
        try:
            value = vcs.getcolormap(value)
        except KeyError:
            raise KeyError('Invalid value {0} for colormap name'.format(value))
        self._real_map = value
        if self._cmap is not None:
            del vcs.elements['colormap'][self._cmap.name]

        self._cmap = vcs.createcolormap(Cp_name_src=self._real_map.name)
        self.update_table()

    def apply(self):
        for ind in range(256):
            self._real_map.index[ind] = self._cmap.index[ind]
        del vcs.elements['colormap'][self._cmap.name]

    def reject(self):
        del vcs.elements['colormap'][self._cmap.name]

    def reset(self):
        for ind in range(256):
            self._cmap.index[ind] = self._real_map.index[ind]
        self.update_table()

    def update_table(self):
        for ind in range(256):
            color = self._cmap.index[ind]
            item = self.item(ind / self.columnCount(), ind % self.columnCount())
            r, g, b, a = [int(2.55 * c) for c in color]
            qcolor = QtGui.QColor(r, g, b, a)
            brush = QtGui.QBrush(qcolor)
            item.setBackground(brush)


if __name__ == "__main__":
    app = QtGui.QApplication([])
    widget = ColormapTable(16)
    widget.cmap = "default"
    widget.show()
    app.exec_()

