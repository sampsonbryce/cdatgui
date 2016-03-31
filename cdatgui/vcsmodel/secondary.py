from .elements import VCSElementsModel
import vcs


class LineElementsModel(VCSElementsModel):
    def __init__(self, parent=None):
        super(LineElementsModel, self).__init__(parent=parent)
        self.el_type = "line"
        self.isa = vcs.isline
        self.get_el = vcs.getline

    def tooltip(self, name, obj):
        return u"Line Primitive '%s'" % obj.name


class TextElementsModel(VCSElementsModel):
    def __init__(self, parent=None):
        # We can skip up above the VCSElementsModel, since we're subverting the standard usage here.
        super(VCSElementsModel, self).__init__(parent=parent)
        self._elements = []

    def get_new_elements(self):
        to = vcs.listelements("textorientation")
        tt = vcs.listelements("texttable")
        text_styles = [el for el in tt if el in to]
        return text_styles

    def get_el(self, name):
        tc = vcs.createtextcombined()
        tc.To = vcs.gettextorientation(name)
        tc.Tt = vcs.gettexttable(name)
        return tc

    def isa(self, obj):
        return vcs.istextcombined(obj) and obj.Tt_name in self.elements and obj.To_name == obj.Tt_name

    def tooltip(self, name, obj):
        return u"Text Style '%s'" % obj.To_name


class FillareaElementsModel(VCSElementsModel):
    def __init__(self, parent=None):
        super(FillareaElementsModel, self).__init__(parent=parent)
        self.el_type = "fillarea"
        self.isa = vcs.isfillarea()
        self.get_el = vcs.getfillarea()

    def tooltip(self, name, obj):
        return u"Fill Primitive '%s'" % obj.name


class MarkerElementsModel(VCSElementsModel):
    def __init__(self, parent=None):
        super(MarkerElementsModel, self).__init__(parent=parent)
        self.el_type = "marker"
        self.isa = vcs.ismarker
        self.get_el = vcs.getmarker

    def tooltip(self, name, obj):
        return u"Marker Primitive '%s'" % obj.name
