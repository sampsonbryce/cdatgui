from PySide import QtGui, QtCore
from directory_widget import DirectoryListWidget


class FileBrowserWidget(QtGui.QWidget):

    selectionChange = QtCore.Signal()

    def __init__(self, root, parent=None, f=0, filetypes=None):
        super(FileBrowserWidget, self).__init__(parent=parent, f=f)

        self.root = QtCore.QDir(root)

        if filetypes is not None:
            # TODO: Filter by file type
            pass

        self.layout = QtGui.QHBoxLayout()
        self.dirs = []
        self.open_directory(self.root)
        self.setLayout(self.layout)

    def open_directory(self, directory):
        dlw = DirectoryListWidget(directory)
        self.layout.addWidget(dlw)
        dlw.currentItemChanged.connect(self.update_selection)
        self.dirs.append(dlw)

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
            self.layout.removeWidget(widget)
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
