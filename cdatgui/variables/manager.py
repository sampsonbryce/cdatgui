import cdms2
import os.path

__man__ = None


def manager():
    global __man__
    if __man__ is None:
        __man__ = Manager()
    return __man__


class Manager(object):

    def __init__(self):
        self.files = {}
        self.file_modified = {}

    def get_file(self, filepath):
        if filepath in self.files:
            return self.files[filepath]
        if not os.path.exists(filepath):
            raise IOError("No data file found at '%s'" % filepath)

        try:
            self.files[filepath] = cdms2.open(filepath)
        except cdms2.CDMSError:
            raise IOError("File at '%s' not of a supported format" % filepath)

        return self.files[filepath]
