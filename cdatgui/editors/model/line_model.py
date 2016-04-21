from .levels_base import LevelsBaseModel
from cdatgui.vcsmodel import get_lines
import vcs


class LineModel(LevelsBaseModel):
    def __init__(self, gm, var, canvas=None):
        self._gm = gm
        self._var = var
        self._canvas = canvas
        self.count = 1

    @property
    def line(self):
        print "LINELIST", self._gm.line
        while len(self._gm.line) < len(self._gm.levels):
            while True:
                try:
                    old_line = vcs.getline(self._gm.line[-1])

                    name = "line_{0}".format(self.count)
                    new_line = vcs.createline(str(name))
                    new_line.type = old_line.type
                    new_line.color = old_line.color
                    new_line.width = old_line.width
                    get_lines().updated(name)
                    self.count += 1
                    break
                except vcs.vcsError as e:
                    self.count += 1
            self._gm.line.append(new_line.name)
        while len(self._gm.line) > len(self._gm.levels):
            self._gm.line.remove(self._gm.line[-1])
        return self._gm.line

    @property
    def linecolors(self):
        return self._gm.linecolors

    @property
    def linewidths(self):
        return self._gm.linewidths

