from .elements import VCSElementsModel
import vcs


class LineElementsModel(VCSElementsModel):
    el_type = "line"

    def __init__(self):
        super(LineElementsModel, self).__init__()
        self.isa = vcs.isline
        self.get_el = vcs.getline

    def tooltip(self, name, obj):
        return u"Line Primitive '%s'" % obj.name


class TextElementsModel(VCSElementsModel):
    def __init__(self):
        self.elements = []
        self.init_elements()
        super(VCSElementsModel, self).__init__()

    def init_elements(self):
        to = vcs.listelements("textorientation")
        tt = vcs.listelements("texttable")
        self.elements = sorted((el for el in tt if el in to))

    def get_el(self, name):
        tt = vcs.gettexttable(name)
        to = vcs.gettextorientation(name)

        for tc in vcs.listelements("textcombined"):
            tc = vcs.gettextcombined(tc)
            if tc.To_name == name and tc.Tt_name == name:
                return tc

        tc = vcs.createtextcombined()
        tc.Tt = tt
        tc.To = to

        return tc

    def isa(self, obj):
        return vcs.istextcombined(obj) and obj.Tt_name in self.elements and obj.To_name == obj.Tt_name

    def tooltip(self, name, obj):
        return u"Text Style '%s'" % obj.To_name


class FillareaElementsModel(VCSElementsModel):
    el_type = "fillarea"

    def __init__(self):
        super(FillareaElementsModel, self).__init__()
        self.isa = vcs.isfillarea
        self.get_el = vcs.getfillarea

    def tooltip(self, name, obj):
        return u"Fill Primitive '%s'" % obj.name


class MarkerElementsModel(VCSElementsModel):
    el_type = "marker"

    def __init__(self):
        super(MarkerElementsModel, self).__init__()
        self.isa = vcs.ismarker
        self.get_el = vcs.getmarker

    def tooltip(self, name, obj):
        return u"Marker Primitive '%s'" % obj.name
