from PySide import QtGui, QtCore
from directory_widget import DirectoryListWidget


class FileBrowserWidget(QtGui.QScrollArea):

    selectionChange = QtCore.Signal()

    def __init__(self, root, parent=None, filetypes=None):
        super(FileBrowserWidget, self).__init__(parent=parent)

        self.root = QtCore.QDir(root)

        self.filetypes = filetypes

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
        """
        Pushes a new DLW based on directory to the end of the layout
        """
        dlw = DirectoryListWidget(directory, filetypes=self.filetypes)
        dlw.setMinimumWidth(200)
        dlw.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Policy.Preferred,
                                            QtGui.QSizePolicy.Policy.Maximum))

        self.container.addWidget(dlw)
        dlw.currentItemChanged.connect(self.update_selection)
        self.dirs.append(dlw)

    def move_to_right(self, min, max):
        """
        As we add/remove items from self, scroll to the right edge
        """
        self.horizontalScrollBar().setValue(max)  # pragma: no cover

    def set_root(self, path):
        """
        Update the widget to use a different root path
        """
        self.root = QtCore.QDir(path)
        self.remove_directories(0)
        self.open_directory(self.root)

    def get_selected_files(self):
        """
        Returns a list of selected files (currently 0 or 1 items)
        """
        last = self.dirs[-1]

        file_info = last.selected_file_info()

        if file_info is None:
            return []
        else:
            if file_info.isDir():  # pragma: no cover
                return []
            else:
                return [file_info.filePath()]

    def remove_directories(self, index):
        """
        Remove every directory >= index from the layout
        """
        for widget in self.dirs[index:]:
            # Clean up the widget
            widget.currentItemChanged.disconnect(self.update_selection)
            self.container.removeWidget(widget)
            widget.deleteLater()
        self.dirs = self.dirs[:index]

    def update_selection(self, current, previous):
        seeking = None

        # We need to figure out which DLW sent this event
        if current is None:
            if previous is None:
                # If both are none, then there's nothing to do
                # This probably can't happen, but I like to be cautious.
                return  # pragma: no cover
            else:
                # We'll search for the previous value
                seeking = previous
        else:
            # We'll search for the new value
            seeking = current

        for ind, widget in enumerate(self.dirs):
            # As soon as we find the right widget, we can stop looking
            if widget.has_item(seeking):
                break
        else:
            # If we can't find a widget that owns the item, we should bail.
            # Probably can't happen, better safe than sorry.
            return  # pragma: no cover

        if ind < len(self.dirs) - 1:
            # Remove everything that comes after the directory
            self.remove_directories(ind + 1)

        new_file = widget.selected_file_info()

        # If nothing's selected, we can just emit and be done
        if new_file is None:
            self.selectionChange.emit()
            return

        # Open up a new directory if the selected item was a directory
        if new_file.isDir():
            self.open_directory(QtCore.QDir(new_file.filePath()))

        # Emit the signal
        self.selectionChange.emit()
