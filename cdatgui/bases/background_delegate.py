from PySide import QtGui, QtCore


class BorderHighlightStyleDelegate(QtGui.QStyledItemDelegate):
	def paint(self, painter, option, index):
		bg = index.data(QtCore.Qt.BackgroundRole)
		painter.fillRect(option.rect, bg)
		super(BorderHighlightStyleDelegate, self).paint(painter, option, index)
		if option.state & QtGui.QStyle.State_Selected:
			painter.accept()
			color = QtGui.QColor(76, 177 ,255)
			pen = QtGui.QPen(color, 2, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap, QtCore.Qt.MiterJoin)
			w = pen.width() / 2
			painter.setPen(pen)
			painter.drawRect(option.rect.adjusted(w, w, -w, -w))
			painter.restore()
