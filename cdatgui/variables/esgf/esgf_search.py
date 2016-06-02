from PySide import QtCore, QtGui
from functools import partial

from cdatgui.utils import label
from pyesgf.search import SearchConnection
from cdatgui.variables.esgf.esgf_tree_model import ESGFDatasetTreeModel


class ESGFSearch(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ESGFSearch, self).__init__(parent=parent)
        self.current_dataset_index = 0
        self.filters = []
        self.conn = SearchConnection('http://esg.ccs.ornl.gov/esg-search', distrib=True)

        add_button = QtGui.QPushButton('Add Filter')
        add_button.clicked.connect(self.addFilter)

        self.search_button = QtGui.QPushButton('Search')
        self.search_button.clicked.connect(self.search)

        self.results_tree = QtGui.QTreeView()

        self.vertical_layout = QtGui.QVBoxLayout()
        self.vertical_layout.addWidget(label('Filters'))
        self.vertical_layout.addWidget(add_button)
        self.vertical_layout.addStretch(1)
        self.vertical_layout.addWidget(self.search_button)
        self.vertical_layout.addWidget(self.results_tree)
        self.setLayout(self.vertical_layout)

        self.addFilter()

    def addFilter(self):
        combo = QtGui.QComboBox()
        combo.addItems(['Project', 'Model', 'Experiment', 'Time Frequency', 'Query'])
        combo.currentIndexChanged[str].connect(partial(self.checkForDuplicateParameters, combo))
        combo.setCurrentIndex(-1)

        edit = QtGui.QLineEdit()
        edit.textChanged.connect(self.update)

        self.filters.append((combo, edit))

        h_layout = QtGui.QHBoxLayout()
        h_layout.addWidget(combo)
        h_layout.addWidget(edit)

        self.vertical_layout.insertLayout(self.vertical_layout.count() - 4, h_layout)
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

    def search(self):
        # self.results_tree.clear()

        constraints = {}
        for combo, edit in self.filters:
            constraints[self.getKeyword(combo.currentText())] = edit.text().strip()
        results = self.conn.send_search(constraints, limit=100)
        data = results["response"]["docs"]
        print "Retrieved", len(data), "records"
        data_model = ESGFDatasetTreeModel(data)
        # data_model.insertRows(0, len(data), data)
        self.results_tree.setModel(data_model)

        '''
        if len(self.cur_data) == 0:
            self.results_tree.addItem('No results')
            return

        for index, dataset in enumerate(self.cur_data):
            if index == 50:
                self.current_dataset_index == 50
                break
            new_item = QtGui.QTreeWidgetItem()
            new_item.setText(0, dataset.dataset_id)
            data_dict = dataset.json

            results = data_dict['variable_long_name']
            for result in results:
                result_item = QtGui.QTreeWidgetItem()
                result_item.setText(0, result)
                new_item.addChild(result_item)

            self.results_tree.addTopLevelItem(new_item)
        '''
