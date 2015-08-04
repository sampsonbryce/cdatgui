from PySide import QtGui, QtCore
from cdatgui.utils import header_label

default_flags = QtCore.QDir.AllEntries | QtCore.QDir.NoDotAndDotDot


class FileInfoItem(QtGui.QListWidgetItem):
    def __init__(self, fileinfo):
        super(FileInfoItem, self).__init__()

        provider = QtGui.QFileIconProvider()

        self.setIcon(provider.icon(fileinfo))
        self.setText(fileinfo.fileName())


class DirectoryListWidget(QtGui.QWidget):

    currentItemChanged = QtGui.QListWidget.currentItemChanged

    def __init__(self, directory, parent=None, f=0, filters=None):
        super(DirectoryListWidget, self).__init__(parent=parent, f=f)

        # An instance of QDir
        self.dir = directory

        # Set sorting to name, case insensitive
        self.dir.setSorting(QtCore.QDir.SortFlag.Name |
                            QtCore.QDir.SortFlag.IgnoreCase |
                            QtCore.QDir.SortFlag.LocaleAware)

        self.list = QtGui.QListWidget()

        self.title = header_label(directory.dirName())

        self.files = []

        for fileinfo in self.dir.entryInfoList(default_flags):
            path = fileinfo.filePath()
            self.files.append(path)
            self.list.addItem(FileInfoItem(fileinfo))

        self.list.currentItemChanged.connect(self.currentItemChanged.emit)

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list)
        self.setLayout(self.layout)

    def selected_file_info(self):
        index = self.list.currentRow()

        if index == -1:
            return None

        file_info = self.dir.entryInfoList(default_flags)[index]
        return file_info

    def has_item(self, item):
        return self.list.row(item) >= 0
