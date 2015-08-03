from PySide import QtGui, QtCore
from cdatgui.utils import header_label


class FileInfoItem(QtGui.QListWidgetItem):
    def __init__(self, fileinfo):
        super(FileInfoItem, self).__init__()

        provider = QtGui.QFileIconProvider()

        self.setIcon(provider.icon(fileinfo))
        self.setText(fileinfo.fileName())


class DirectoryListWidget(QtGui.QWidget):
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

        for fileinfo in self.dir.entryInfoList():
            path = fileinfo.filePath()
            self.files.append(path)
            self.list.addItem(FileInfoItem(fileinfo))

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.list)
        self.setLayout(self.layout)
