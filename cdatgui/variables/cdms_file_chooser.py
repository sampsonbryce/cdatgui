import urllib
from PySide import QtGui, QtCore
from cdatgui.bases import VerticalTabWidget, FileBrowserWidget
from manager import manager
from cdatgui.variables.esgf.esgf_search import ESGFSearch


class CDMSFileChooser(QtGui.QDialog):

    def __init__(self, parent=None, f=0):
        super(CDMSFileChooser, self).__init__(parent=parent, f=f)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.tabs = VerticalTabWidget()

        self.layout = QtGui.QVBoxLayout()

        self.setLayout(self.layout)
        self.local_buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                         QtGui.QDialogButtonBox.Cancel)

        self.local_buttons.accepted.connect(self.accept)
        self.local_buttons.rejected.connect(self.reject)

        self.accepted_button = self.local_buttons.button(QtGui.QDialogButtonBox.Ok)
        self.accepted_button.setEnabled(False)
        
        # self.esgf_buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Cancel)
        # import_as = QtGui.QPushButton('Import')
        # import_as.clicked.connect(self.accept)
        # self.esgf_buttons.addButton(import_as, QtGui.QDialogButtonBox.AcceptRole)

        self.layout.addWidget(self.tabs, 10)
        self.layout.addWidget(self.local_buttons)

        # Add different methods for opening files here
        self.file_browser = FileBrowserWidget("/", filetypes=["nc"])
        self.file_browser.selectionChange.connect(self.selected_files)

        self.esgf_search = ESGFSearch()
        self.esgf_search.selectionChange.connect(self.selectedESGFDatasets)

        self.tabs.add_widget(u"Local File", self.file_browser)
        self.tabs.add_widget(u"ESGF", self.esgf_search)

    '''def adjustForESGF(self):
        self.layout.takeAt(self.layout.count() - 1)
        self.layout.addWidget(self.esgf_buttons)
        return self.esgf_search
    '''

    def selectedESGFDatasets(self):
        print "getting datasets"
        data = self.esgf_search.getSelectedDataset()
        print "data", data
        if data is None:
            self.accepted_button.setEnabled(False)
            return
        else:
            self.accepted_button.setEnabled(True)

    def selected_files(self):
        files = self.file_browser.get_selected_files()
        if len(files) == 0:
            self.accepted_button.setEnabled(False)
        else:
            self.accepted_button.setEnabled(True)

    def get_selected(self):
        if self.tabs.current_row() == 0:  # local
            files = []
            for fpath in self.file_browser.get_selected_files():
                files.append(manager().get_file(fpath))
            return files

        if self.tabs.current_row() == 1:  # ESGF
            data = self.esgf_search.getSelectedDataset()
            if data is None:
                raise Exception('Something bad happened')

            file_results = data.file_context().search()
            f = file_results[0]
            print f.download_url
            # for f in file_results:
            stuff = urllib.urlretrieve(f.download_url, "mp3.mp3")
            return []
