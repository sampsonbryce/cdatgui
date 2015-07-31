from PySide import QtGui


class VerticalTabWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(VerticalTabWidget, self).__init__(parent=parent)
        layout = QtGui.QHBoxLayout()

        self.list = QtGui.QListWidget()
        self.display = QtGui.QStackedLayout()

        layout.addWidget(self.list, 3)
        layout.addLayout(self.display, 7)

        self.setLayout(layout)

        self.list.itemClicked.connect(self.itemClicked)

    def addWidget(self, title, widget):
        self.list.addItem(title)
        self.display.addWidget(widget)

    def addLayout(self, title, layout):
        self.list.addItem(title)
        self.display.addLayout(layout)

    def itemClicked(self, item):
        self.display.setCurrentIndex(self.list.currentRow())

    def currentRow(self):
        return self.list.currentRow()
