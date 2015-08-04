from PySide import QtGui, QtCore
from directory_widget import DirectoryListWidget


class FileBrowserWidget(QtGui.QScrollArea):

    selectionChange = QtCore.Signal()

    def __init__(self, root, parent=None, filetypes=None):
        super(FileBrowserWidget, self).__init__(parent=parent)

        self.root = QtCore.QDir(root)

        if filetypes is not None:
            # TODO: Filter by file type
            pass

        self.container = QtGui.QHBoxLayout()
        self.container.setSpacing(0)

        parent = QtGui.QWidget()
        parent.setLayout(self.container)
        self.setWidget(parent)
        self.setWidgetResizable(True)
        self.horizontalScrollBar().rangeChanged.connect(self.move_to_right)

        self.dirs = []
        self.open_directory(self.root)

    def open_directory(self, directory):
        dlw = DirectoryListWidget(directory)
        dlw.setMinimumWidth(200)
        dlw.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Policy.Preferred,
                                            QtGui.QSizePolicy.Policy.Maximum))

        self.container.addWidget(dlw)
        dlw.currentItemChanged.connect(self.update_selection)
        self.dirs.append(dlw)

    def move_to_right(self, min, max):
        self.horizontalScrollBar().setValue(max)

    def set_root(self, path):
        self.root = QtCore.QDir(path)
        self.remove_directories(0)
        self.open_directory(self.root)

    def get_selected_files(self):
        selected = []

        last = self.dirs[-1]

        file_info = last.selected_file_info()

        if file_info is None:
            return []
        else:
            if file_info.isDir():
                return []
            else:
                return [file_info.filePath()]

        return selected

    def remove_directories(self, index):
        """
        index is the start of the section to cut off the end
        """
        for widget in self.dirs[index:]:
            widget.currentItemChanged.disconnect(self.update_selection)
            self.container.removeWidget(widget)
            widget.setParent(None)
        self.dirs = self.dirs[:index]

    def update_selection(self, current, previous):
        seeking = None

        if current is None:
            if previous is None:
                return
            else:
                seeking = previous
        else:
            seeking = current

        for ind, widget in enumerate(self.dirs):
            if widget.has_item(seeking):
                break
        else:
            return

        if ind < len(self.dirs) - 1:
            self.remove_directories(ind + 1)

        new_file = widget.selected_file_info()

        if new_file is None:
            self.selectionChange.emit()
            return

        if new_file.isDir():
            self.open_directory(QtCore.QDir(new_file.filePath()))

        self.selectionChange.emit()
