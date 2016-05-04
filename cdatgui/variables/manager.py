import cdms2
from cdatgui.persistence.db import get_data_sources, add_data_source, remove_data_source
import cdatgui.cdat.metadata
from PySide import QtCore

__man__ = None


def update_db(f):
    add_data_source(f.uri)


def manager():
    global __man__
    if __man__ is None:
        __man__ = Manager(initial_uris=get_data_sources())
        __man__.usedFile.connect(update_db)
    return __man__


class Manager(QtCore.QObject):

    addedFile = QtCore.Signal(object)
    usedFile = QtCore.Signal(object)

    def __init__(self, initial_uris=None):
        super(Manager, self).__init__()
        self.files = {}

        if initial_uris is not None:
            for uri in initial_uris:
                self.add_file(cdms2.open(uri))

    def get_file(self, uri):
        if uri not in self.files:
            f = cdms2.open(uri)
            return self.add_file(f)

        self.usedFile.emit(self.files[uri])
        return self.files[uri]

    def add_file(self, file):
        if file.uri in self.files:
            fmw = self.files[file.uri]
        else:
            fmw = cdatgui.cdat.metadata.FileMetadataWrapper(file)
            self.files[file.uri] = fmw

        self.addedFile.emit(fmw)
        self.usedFile.emit(fmw)

        return fmw

    def remove_file(self, file):
        if file.uri not in self.files:
            raise Exception("File not in manager.")
        del self.files[file.uri]
        remove_data_source(file.uri)
