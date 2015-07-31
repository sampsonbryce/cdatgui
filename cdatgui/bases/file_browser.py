from PySide import QtGui, QtCore


class FileBrowserWidget(QtGui.QWidget):
    selectionChange = QtCore.Signal()

    def __init__(self, root, parent=None, f=0, filetypes=None):
        super(FileBrowserWidget, self).__init__(parent=parent, f=f)

        self.file_model = QtGui.QFileSystemModel(self)
        self.file_model.setRootPath(root)

        if filetypes is not None:
            # TODO: Filter by file type
            pass

        self.file_tree = QtGui.QTreeView(self)
        self.file_tree.setModel(self.file_model)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.file_tree, 10)

        self.setLayout(layout)

        self.file_tree.clicked.connect(self.selection)

    def set_root(self, path):
        self.file_model.setRootPath(path)

    def get_selected_files(self):
        selected = []
        for ind in self.file_tree.selectedIndexes():
            selected.append(self.file_model.filePath(ind))
        return selected

    def selection(self, index):
        self.selectionChange.emit()
