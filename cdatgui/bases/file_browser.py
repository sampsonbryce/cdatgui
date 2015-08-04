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

        # Update the display widgets
        for widget in self.dirs:
            self.layout.removeWidget(widget)

        self.dirs = []
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

    def update_selection(self, current, previous):
        print "hi"
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
            # Need to remove everything after widget
            for widget in self.dirs[ind + 1:]:
                self.layout.removeWidget(widget)
            self.dirs = self.dirs[:ind + 1]

        new_file = widget.selected_file_info()

        if new_file.isDir():
            self.open_directory(QtCore.QDir(new_file.filePath()))

        self.selectionChange.emit()
