from PySide import QtGui, QtCore
from cdatgui.bases import VerticalTabWidget, FileBrowserWidget
from manager import manager


class CDMSFileChooser(QtGui.QDialog):

    def __init__(self, parent=None, f=0):
        super(CDMSFileChooser, self).__init__(parent=parent, f=f)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.tabs = VerticalTabWidget()

        layout = QtGui.QVBoxLayout()

        self.setLayout(layout)
        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                         QtGui.QDialogButtonBox.Cancel)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.accepted_button = buttons.button(QtGui.QDialogButtonBox.Ok)
        self.accepted_button.setEnabled(False)

        layout.addWidget(self.tabs, 10)
        layout.addWidget(buttons)

        # Add different methods for opening files here
        self.file_browser = FileBrowserWidget("/", filetypes=["nc"])
        self.file_browser.selectionChange.connect(self.selected_files)

        self.tabs.add_widget(u"Local File", self.file_browser)

    def selected_files(self):
        files = self.file_browser.get_selected_files()
        if len(files) == 0:
            self.accepted_button.setEnabled(False)
        else:
            self.accepted_button.setEnabled(True)

    def get_selected(self):
        if self.tabs.current_row() == 0:
            files = []
            for fpath in self.file_browser.get_selected_files():
                files.append(manager().get_file(fpath))
            return files
