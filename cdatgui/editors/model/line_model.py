from .levels_base import LevelsBaseModel
from cdatgui.vcsmodel import get_lines
import vcs


class LineModel(LevelsBaseModel):
    def __init__(self, gm, var, canvas=None):
        print "CREATING LINE MODEL"
        self._gm = gm
        self._var = var
        self._canvas = canvas
        self.count = 1

    @property
    def line(self):
        while len(self._gm.line) < len(self._gm.levels):
            self._gm.line.append(self._gm.line[-1])
        while len(self._gm.line) > len(self._gm.levels):
            self._gm.line.remove(self._gm.line[-1])
        print "RETURNING:", self._gm.line
        return self._gm.line

    @property
    def linecolors(self):
        return self._gm.linecolors

    @property
    def linewidths(self):
        return self._gm.linewidths

