from .levels_base import LevelsBaseModel
from cdatgui.vcsmodel import get_textstyles
import vcs


class IsolineModel(LevelsBaseModel):
    def __init__(self, gm, var, canvas=None):
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
        return self._gm.line

    @property
    def linecolors(self):
        return self._gm.linecolors

    @property
    def linewidths(self):
        return self._gm.linewidths

    @property
    def text(self):
        if not self._gm.text:
            self._gm.text = ['default']
        while len(self._gm.text) < len(self._gm.levels):
            self._gm.text.append(self._gm.text[-1])
        while len(self._gm.text) > len(self._gm.levels):
            self._gm.text.remove(self._gm.text[-1])
        return self._gm.text

    @property
    def textcolors(self):
        return self._gm.textcolors
