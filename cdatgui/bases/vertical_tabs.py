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

        self.is_layout = []

        self.list.currentItemChanged.connect(self.current_changed)

    def add_widget(self, title, widget):
        self.list.addItem(title)
        if self.list.count() == 1:
            self.list.setCurrentRow(0)
        self.display.addWidget(widget)

    def add_layout(self, title, layout):
        widget_wrapper = QtGui.QWidget()
        widget_wrapper.setLayout(layout)

        self.is_layout.append(self.display.count())

        self.add_widget(title, widget_wrapper)

    def item(self, index):
        item_title = self.list.item(index).text()

        item = self.display.widget(index)

        if index in self.is_layout:
            item = item.layout()

        return item_title, item

    def current_changed(self, current, previous):
        self.display.setCurrentIndex(self.list.currentRow())

    def current_item(self):
        text = self.list.currentItem().text()
        item = self.display.currentWidget()

        if self.display.currentIndex() in self.is_layout:
            item = item.layout()

        return text, item

    def current_row(self):
        return self.list.currentRow()

    def set_current_row(self, index):
        self.list.setCurrentRow(index)
