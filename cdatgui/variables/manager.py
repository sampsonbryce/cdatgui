import cdms2
from cdatgui.persistence.db import get_data_sources, add_data_source
import cdatgui.cdat
from PySide import QtCore

__man__ = None


def manager():
    global __man__
    if __man__ is None:
        __man__ = Manager()
    return __man__


class Manager(QtCore.QObject):

    addedFile = QtCore.Signal(object)

    def __init__(self):
        super(Manager, self).__init__()
        self.files = {}

        uris = get_data_sources()
        for uri in uris:
            self.add_file(cdms2.open(uri))

    def get_file(self, uri):
        if uri not in self.files:
            return self.add_file(cdatgui.cdat.FileMetadataWrapper(cdms2.open(uri)))

        add_data_source(uri)
        return self.files[uri]

    def add_file(self, file):
        if file.uri in self.files:
            self.addedFile.emit(self.files[file.uri])
            return self.files[file.uri]

        self.files[file.uri] = cdatgui.cdat.FileMetadataWrapper(file)
        add_data_source(file.uri)
        self.addedFile.emit(self.files[file.uri])
        return self.files[file.uri]
