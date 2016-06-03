from PySide import QtCore, QtGui
from functools import partial

from cdatgui.utils import label
from pyesgf.search import SearchConnection
from pyesgf.logon import LogonManager
from cdatgui.variables.esgf.esgf_tree_model import ESGFDatasetTreeModel
import gc, time, urllib


class ESGFSearch(QtGui.QWidget):
    selectionChange = QtCore.Signal()

    def __init__(self, parent=None):
        super(ESGFSearch, self).__init__(parent=parent)
        self.current_dataset_index = 0
        self.filters = []
        self.conn = SearchConnection('http://esg.ccs.ornl.gov/esg-search', distrib=True)
        self.current_offset = 0
        self.current_limit = 100
        self.results = None

        add_button = QtGui.QPushButton('Add Filter')
        add_button.clicked.connect(self.addFilter)

        self.search_button = QtGui.QPushButton('Search')
        self.search_button.clicked.connect(self.search)

        self.results_tree = QtGui.QTreeView()
        self.results_tree.clicked.connect(self.emitSelectionChange)

        self.limit = QtGui.QSpinBox()
        self.limit.setMinimum(1)
        self.limit.setMaximum(10000)
        self.limit.setValue(100)

        self.offset = QtGui.QSpinBox()
        self.offset.setValue(0)
        self.offset.setMaximum(100000)

        spin_layout = QtGui.QHBoxLayout()
        spin_layout.addWidget(label('Limit:'))
        spin_layout.addWidget(self.limit)
        spin_layout.addWidget(label('Offset:'))
        spin_layout.addWidget(self.offset)

        self.next_page_button = QtGui.QPushButton('Next Page')
        self.next_page_button.setEnabled(False)
        self.next_page_button.clicked.connect(self.nextPage)

        self.prev_page_button = QtGui.QPushButton('Prev Page')
        self.prev_page_button.setEnabled(False)
        self.prev_page_button.clicked.connect(self.prevPage)

        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.prev_page_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.next_page_button)

        self.vertical_layout = QtGui.QVBoxLayout()
        self.vertical_layout.addWidget(label('Filters'))
        self.vertical_layout.addWidget(add_button)
        self.vertical_layout.addWidget(self.search_button)
        self.vertical_layout.addLayout(spin_layout)
        self.vertical_layout.addWidget(self.results_tree)
        self.vertical_layout.addLayout(button_layout)
        self.setLayout(self.vertical_layout)

        self.addFilter()

    def emitSelectionChange(self):
        print 'emitting'
        self.selectionChange.emit()

    def addFilter(self):
        combo = QtGui.QComboBox()
        combo.addItems(
            ['Project', 'Model', 'Experiment', 'Time Frequency', 'Query', 'Realm', 'Ensemble', 'From Timestamp',
             'To Timestamp', 'Experiement', 'Experiment Family'])
        combo.currentIndexChanged[str].connect(partial(self.checkForDuplicateParameters, combo))
        combo.setCurrentIndex(-1)

        edit = QtGui.QLineEdit()
        edit.textChanged.connect(self.update)

        self.filters.append((combo, edit))

        h_layout = QtGui.QHBoxLayout()
        h_layout.addWidget(combo)
        h_layout.addWidget(edit)

        self.vertical_layout.insertLayout(self.vertical_layout.count() - 5, h_layout)
        self.update()

    def checkForDuplicateParameters(self, cur_combo, text):
        for combo, _ in self.filters:
            if combo != cur_combo:
                if combo.currentText() == text:
                    combo.setCurrentIndex(-1)

        self.update()

    def update(self, *args):
        for combo, edit in self.filters:
            if combo.currentIndex() == -1:
                self.search_button.setEnabled(False)
                return
            if edit.text() == '':
                self.search_button.setEnabled(False)
                return
        else:
            self.search_button.setEnabled(True)

    def getKeyword(self, value):
        if value == 'Project':
            return 'project'
        if value == 'Model':
            return 'model'
        if value == 'Experiment':
            return 'experiment'
        if value == 'Time Frequency':
            return 'time_frequency'
        if value == 'Query':
            return 'query'
        if value == 'Realm':
            return 'realm'
        if value == 'Ensemble':
            return 'ensemble'
        if value == 'From Timestamp':
            return 'from_timestamp'
        if value == 'To Timestamp':
            return 'to_timestamp'
        if value == 'Experiment':
            return 'experiment'
        if value == 'Experiment Family':
            return 'experiment_family'



    def prevPage(self):
        self.current_offset -= self.current_limit
        self.next_page_button.setEnabled(True)
        self.updateResults()

    def nextPage(self):
        self.current_offset += self.current_limit
        self.prev_page_button.setEnabled(True)
        self.updateResults()

    def verifyValues(self):
        if self.current_offset <= 0:
            self.current_offset = 0
            self.prev_page_button.setEnabled(False)
        else:
            self.prev_page_button.setEnabled(True)

        if self.endPosition() == len(self.results):
            self.next_page_button.setEnabled(False)
        else:
            self.next_page_button.setEnabled(True)

    def updateResults(self):
        self.verifyValues()
        data = []
        gc.disable()
        for i in range(self.current_offset, self.endPosition()):
            item = self.results[i]
            data.append(item)
        gc.enable()
        self.results_tree.model().setDatasets(data)
        self.selectionChange.emit()

    def endPosition(self):
        position = self.current_offset + self.current_limit
        if position > len(self.results):
            position = len(self.results)
        return position

    def search(self):
        constraints = {}
        for combo, edit in self.filters:
            constraints[self.getKeyword(combo.currentText())] = edit.text().strip()
        self.current_limit = self.limit.value()
        self.current_offset = self.offset.value()
        print "constraints", constraints
        ctx = self.conn.new_context(**constraints)
        self.results = ctx.search()
        print 'Record count', len(self.results)
        print 'off, end', self.current_offset, self.endPosition()
        end_position = self.endPosition()
        if end_position == 0:
            QtGui.QMessageBox.information(self, 'No results', 'No Results')
            return
        data = []
        for i in range(self.current_offset, end_position):
            data.append(self.results[i])

        data_model = ESGFDatasetTreeModel(data)
        self.results_tree.setModel(data_model)

        self.next_page_button.setEnabled(True)

    def getSelectedDataset(self):
        selected_index = self.results_tree.selectedIndexes()[0]
        if selected_index.parent().isValid():
            return None
        else:
            return self.results_tree.model().getDataset(selected_index)

